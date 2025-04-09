import os
import gradio as gr
import tempfile
import shutil
import psycopg2
import math
import sys
sys.path.append('.')
from app import app_query
from dejavu import Dejavu

config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}
source_dir = app_query.data_source_index_dir  # hoặc nơi bạn lưu nhiều thư mục chứa nhạc

# Khởi tạo Dejavu
djv = Dejavu(config)

# ---------- Cấu hình phân trang ----------
PAGE_SIZE = 25

# ---------- Lấy danh sách bài hát từ DB ----------


def fetch_songs(keyword=""):
    try:
        conn = psycopg2.connect(**config['database'])
        cur = conn.cursor()
        if keyword:
            cur.execute("SELECT song_name FROM songs WHERE song_name ILIKE %s ORDER BY song_name", (f"%{keyword}%",))
        else:
            cur.execute("SELECT song_name FROM songs ORDER BY song_name")
        songs = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return songs
    except Exception as e:
        return f"❌ Lỗi database: {e}"

# ---------- Tải trang hiện tại ----------


def get_paged_songs(page, keyword):
    all_songs = fetch_songs(keyword)
    if isinstance(all_songs, str):
        return all_songs, 1, ""

    total_pages = max(1, math.ceil(len(all_songs) / PAGE_SIZE))
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    songs_page = all_songs[start:end]

    content = "\n".join(f"{start + i + 1}. {name}" for i, name in enumerate(songs_page))
    return content or "📭 Không có kết quả.", total_pages, f"Trang {page}/{total_pages}"

# ---------- Index thư mục ----------
def find_common_files(folder1, folder2):
    files1 = {f for f in os.listdir(folder1) if f.endswith((".mp3", ".wav"))}
    files2 = {f for f in os.listdir(folder2) if f.endswith((".mp3", ".wav"))}
    return list(files1.intersection(files2))
def list_folders(base_path):
    if not os.path.exists(base_path):
        return []
    return [
        name for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]
def index_folder_gradio(folder_name):
    folder_path = os.path.join(source_dir, folder_name)
    if not os.path.exists(folder_path):
        return "❌ Thư mục không tồn tại.", ""

    try:
        # Tìm file trùng tên
        common_files = find_common_files(folder_path, app_query.data_dir)
        if common_files:
            common_list = "\n".join(f"⚠️ {name}" for name in common_files)
            return "⚠️ Có file trùng tên, không index.", common_list

        # Index
        djv.fingerprint_directory(folder_path, [".mp3", ".wav"], 4)

        # Copy file
        for file_name in os.listdir(folder_path):
            if file_name.endswith((".mp3", ".wav")):
                src = os.path.join(folder_path, file_name)
                dst = os.path.join(app_query.data_dir, file_name)
                shutil.copy2(src, dst)

        return "✅ Đã index và copy file thành công!", "✅ Không có file trùng tên."
    except Exception as e:
        return f"❌ Lỗi khi index: {str(e)}", ""


def display_matched_segments(results, result_dir, data_dir, recognize_file):
    html_segments = ""

    for idex_s, value in enumerate(results.matches):
        song_name = value.song_name.decode('utf-8')
        song_path = os.path.join(data_dir, song_name)
        songs = [song_path, recognize_file]

        for song_q in value.offsets:
            for idex, song_seg in enumerate(song_q):
                html_segments += f"<strong>🎶 Bài hát: {song_name}</strong><br>"
                html_segments+="<div style='display: flex; flex-direction: row; margin-bottom: 20px;'>"
                for idx2, song in enumerate(song_seg.all()):
                    file_out = os.path.join(
                        result_dir,
                        f"s{idex_s}_c{song_seg.count}_{song_name}_seg{idex}_{idx2}_{song.start_time}_{song.end_time}.mp3"
                    )
                    label = "Bản gốc" if idx2 == 0 else "Query"
                    html_segments += f"""
                    <div style="margin-bottom: 20px;">
                        <strong>🎯 Đoạn {idex_s}.{idex}.{idx2} ({label}):</strong><br>
                        <span>🕒 {song.start_time}s → {song.end_time}s</span><br>
                        <audio controls src="/file={file_out}"></audio>
                    </div>
                    """
                html_segments+="</div>"
                

    # Thêm scroll box
    scroll_box = f"""
    <div style="max-height: 500px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
        {html_segments}
    </div>
    """
    return gr.HTML(scroll_box)


def run_and_display_segments(file):
    is_match, results = app_query. match_and_save_segments(djv, file, app_query.data_dir, app_query.result_dir)
    if is_match:
        return display_matched_segments(results, app_query.result_dir, app_query. data_dir, file)
    else:
        return [gr.Markdown("⚠️ Không tìm thấy đoạn nào trùng khớp.")]
    
def update_folder_choices():
    folders = list_folders(source_dir)
    return gr.update(choices=folders)


#delete song
def delete_song(song_name):
    try:
        conn = psycopg2.connect(**config['database'])
        cur = conn.cursor()

        # Xóa trong DB
        # cur.execute("DELETE FROM fingerprints WHERE song_id = (SELECT id FROM songs WHERE song_name = %s)", (song_name,))
        cur.execute("DELETE FROM songs WHERE song_name = %s", (song_name,))
        conn.commit()

        cur.close()
        conn.close()

        # Xóa file vật lý nếu tồn tại
        file_path = os.path.join(app_query.data_dir, song_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        return f"🗑️ Đã xóa bài: {song_name}"
    except Exception as e:
        return f"❌ Lỗi khi xóa: {e}"
def delete_and_update(song_name):
    result = delete_song(song_name)
    updated_songs = fetch_songs()
    return result, gr.update(choices=updated_songs)
# ---------- Giao diện Gradio ----------
with gr.Blocks(title="Dejavu Audio Fingerprint 🎼") as app:
    
    gr.Markdown("## 🎵 Dejavu Audio Fingerprint App")

    with gr.Tabs():
        # --- Tab 1: Quản lý bài hát ---
        with gr.TabItem("♫ Quản lý bài hát"):
            gr.Markdown("### 🎶 Danh sách bài hát đã index")
            with gr.Row():
                delete_dropdown = gr.Dropdown(choices=fetch_songs(), label="🎵 Chọn bài để xoá", interactive=True)
                delete_button = gr.Button("🗑️ Xóa bài")
                delete_result = gr.Textbox(label="Trạng thái xoá", interactive=False)
            with gr.Row():
                keyword_input = gr.Textbox(placeholder="🔍 Tìm kiếm theo tên...", scale=3)
                search_btn = gr.Button("Tìm")

            with gr.Row():
                prev_btn = gr.Button("⬅️ Trước", scale=1)
                next_btn = gr.Button("➡️ Sau", scale=1)
                page_label = gr.Textbox(label="Trang", interactive=False, max_lines=1, scale=2)

            song_output = gr.Textbox(label="Danh sách bài hát", lines=12)
            delete_button.click(fn=delete_and_update, inputs=delete_dropdown, outputs=[delete_result, delete_dropdown])

            current_page = gr.State(1)

            # Callback cập nhật danh sách
            def update_list(page, keyword):
                return get_paged_songs(page, keyword)

            search_btn.click(fn=update_list, inputs=[current_page, keyword_input], outputs=[song_output, current_page, page_label])
            prev_btn.click(lambda p, k: update_list(p - 1, k), inputs=[current_page, keyword_input], outputs=[song_output, current_page, page_label])
            next_btn.click(lambda p, k: update_list(p + 1, k), inputs=[current_page, keyword_input], outputs=[song_output, current_page, page_label])

            # Load mặc định ban đầu
            app.load(fn=update_list, inputs=[current_page, keyword_input], outputs=[song_output, current_page, page_label])
            app.load(fn=lambda: gr.update(choices=fetch_songs()), outputs=delete_dropdown)
        # --- Tab 2: Index thư mục ---
        with gr.TabItem("♪ Index thư mục"):
            gr.Markdown("### 📁 Chọn thư mục để index")
            # folder_input = gr.Textbox(label="Nhập đường dẫn thư mục")
            folder_list = list_folders(source_dir)
            folder_dropdown = gr.Dropdown(choices=folder_list, label="Chọn thư mục")
            with gr.Row():
                index_output = gr.Textbox(label="Trạng thái index", lines=2, interactive=False)
                common_file_output = gr.Textbox(label="🎵 File trùng tên với thư viện", lines=10, interactive=False)

            gr.Button("🎼 Bắt đầu index").click(
                fn=index_folder_gradio,
                inputs=folder_dropdown,
                outputs=[index_output, common_file_output]
            )
            # 👉 Làm mới danh sách thư mục khi F5 / load lại app
            app.load(fn=update_folder_choices, outputs=folder_dropdown)

        # --- Tab 3: Truy vấn bài hát ---

        with gr.Tab("🔎 Truy vấn và phân đoạn"):
            query_input = gr.Audio(label="🎧 File truy vấn", type="filepath")
            match_btn = gr.Button("▶️ Tìm đoạn khớp")
            segment_output = gr.HTML()
            match_btn.click(fn=run_and_display_segments, inputs=query_input, outputs=segment_output)

# Chạy ứng dụng
if __name__ == "__main__":
    gr.set_static_paths(paths=[app_query.result_dir])
    app.launch(server_name="0.0.0.0")
