
# Hàm index chạy trong job
import os
import shutil
import sys

from redis import Redis
from rq import Queue
sys.path.append('.')
from app import app_query
from app.dejavu_web import delete_and_update, display_matched_segments, fetch_songs, find_common_files, get_paged_songs, list_folders
from dejavu import Dejavu
from rq.job import Job
from app import app_query

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

# Cấu hình Redis
redis_conn = Redis(host='redis', port=6379, db=0)
q = Queue(connection=redis_conn)

# Khởi tạo Dejavu
djv = Dejavu(config)
def index_folder_job(folder_name, job_id):
    folder_path = os.path.join(source_dir, folder_name)
    if not os.path.exists(folder_path):
        return "❌ Thư mục không tồn tại.", ""

    try:
        common_files = find_common_files(folder_path, app_query.data_dir)
        if common_files:
            common_list = "\n".join(f"⚠️ {name}" for name in common_files)
            return "⚠️ Có file trùng tên, không index.", common_list

        djv.fingerprint_directory(folder_path, [".mp3", ".wav"], 4)
        for file_name in os.listdir(folder_path):
            if file_name.endswith((".mp3", ".wav")):
                src = os.path.join(folder_path, file_name)
                dst = os.path.join(app_query.data_dir, file_name)
                shutil.copy2(src, dst)

        return "✅ Đã index và copy file thành công!", "✅ Không có file trùng tên."
    except Exception as e:
        return f"❌ Lỗi khi index: {str(e)}", ""

# Hàm query chạy trong job
def query_job(file, job_id):
    is_match, results = app_query.match_and_save_segments(djv, file, app_query.data_dir, app_query.result_dir)
    if is_match:
        return display_matched_segments(results, app_query.result_dir, app_query.data_dir, file)
    return "<p>⚠️ Không tìm thấy đoạn nào trùng khớp.</p>"

# Hàm kiểm tra trạng thái job
def check_job_status(job_id):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        if job.is_finished:
            return job.result, "Hoàn thành"
        elif job.is_failed:
            return "❌ Job thất bại", "Thất bại"
        elif job.is_queued or job.is_started:
            return "⏳ Đang xử lý...", "Đang chạy"
    except:
        return "❓ Không tìm thấy job", "Không xác định"
    
def start_query_job(file):
    job = q.enqueue(query_job, file, job_id=None)
    return job.id, "<p>⏳ Đã thêm vào hàng đợi...</p>"

def update_query_status(job_id):
    result, status = check_job_status(job_id)
    return result if "Hoàn thành" in status else result
def start_index_job(folder_name):
    job = q.enqueue(index_folder_job, folder_name, job_id=None)
    return job.id, "⏳ Đã thêm vào hàng đợi..."

def update_index_status(job_id):
    result, status = check_job_status(job_id)
    if "Hoàn thành" in status:
        return result[0], result[1]
    return result, ""
    # Khôi phục trạng thái khi load lại
def restore_jobs():
    jobs = q.jobs  # Lấy danh sách jobs đang chạy hoặc trong hàng đợi
    if jobs:
        return f"Đã khôi phục {len(jobs)} job(s) đang chạy."
    return "Không có job nào để khôi phục."