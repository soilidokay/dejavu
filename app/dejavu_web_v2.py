import sys
sys.path.append('.')
from app.dejavu_web import delete_and_update, display_matched_segments, fetch_songs, find_common_files, get_paged_songs, list_folders
from app import app_query
import os
import gradio as gr
import tempfile
import shutil
import psycopg2
import math
from redis import Redis
from rq import Queue, Worker
from rq.job import Job

from app.jobs import index_folder_job, restore_jobs, start_index_job, start_query_job, update_index_status, update_query_status

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
source_dir = app_query.data_source_index_dir
djv = Dejavu(config)
PAGE_SIZE = 25

# Hàm fetch_songs, get_paged_songs, find_common_files, list_folders giữ nguyên...


# Giao diện Gradio
with gr.Blocks(title="Dejavu Audio Fingerprint 🎼") as app:
    gr.Markdown("## 🎵 Dejavu Audio Fingerprint App")

    with gr.Tabs():
        # Tab Quản lý bài hát (giữ nguyên)
        with gr.TabItem("♫ Quản lý bài hát"):
            # Code giữ nguyên như cũ...
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
        # Tab Index thư mục
        with gr.TabItem("♪ Index thư mục"):
            gr.Markdown("### 📁 Chọn thư mục để index")
            folder_dropdown = gr.Dropdown(choices=list_folders(source_dir), label="Chọn thư mục")
            index_button = gr.Button("🎼 Bắt đầu index")
            index_output = gr.Textbox(label="Trạng thái index", interactive=False)
            common_file_output = gr.Textbox(label="File trùng tên", interactive=False)
            job_id_state = gr.State(None)

            index_button.click(fn=start_index_job, inputs=folder_dropdown, outputs=[job_id_state, index_output])
            gr.Timer(2.0).tick(fn=update_index_status, inputs=job_id_state, outputs=[index_output, common_file_output])

        # Tab Truy vấn
        with gr.Tab("🔎 Truy vấn và phân đoạn"):
            query_input = gr.Audio(label="🎧 File truy vấn", type="filepath")
            match_button = gr.Button("▶️ Tìm đoạn khớp")
            segment_output = gr.HTML()
            query_job_id_state = gr.State(None)

            match_button.click(fn=start_query_job, inputs=query_input, outputs=[query_job_id_state, segment_output])
            gr.Timer(2.0).tick(fn=update_query_status, inputs=query_job_id_state, outputs=segment_output)



    app.load(fn=restore_jobs, outputs=gr.Textbox(label="Trạng thái khôi phục"))

if __name__ == "__main__":
    gr.set_static_paths(paths=[app_query.result_dir])
    app.launch(server_name="0.0.0.0")
