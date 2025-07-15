from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import uuid, os, tempfile

app = Flask(__name__)
app.secret_key = "change_me"  # غيّرها إلى قيمة أقوى في الإنتاج

# مسار مؤقّت للتنزيلات
TMP_DIR = tempfile.gettempdir()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("video_url", "").strip()
        if not url:
            flash("أدخل رابطاً صالحاً", "danger")
            return redirect(url_for("index"))

        # اسم ملف فريد لتجنّب التضارب
        out_path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.%(ext)s")
        ydl_opts = {
            "outtmpl": out_path,
            "format": "best[ext=mp4]/best",
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            flash(f"فشل التحميل: {e}", "danger")
            return redirect(url_for("index"))

        # ابحث عن الملف الذي تم تنزيله فعلياً
        prefix = os.path.basename(out_path).split(".%(ext)s")[0]
        for fname in os.listdir(TMP_DIR):
            if fname.startswith(prefix):
                file_path = os.path.join(TMP_DIR, fname)
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=fname
                )

        flash("لم يعثر على الملف بعد التنزيل", "danger")
        return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    # استمع على جميع الواجهات port=5000 وفعّل إعادة التحميل التلقائي
    app.run(host="0.0.0.0", port=5000, debug=True)
