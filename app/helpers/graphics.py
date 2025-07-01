import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# graphics menyediakan fungsi2 untuk render dataviz


def generate_heatmap(cm, labels):
    # 1 | konfigurasi canvas dan render heatmap
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels) # render heatmap

    # 2 | konfigurasi labels
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    # 3 | simpan ke buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)

    # 4 | encode gambar menjadi base64, agar dapat disend sebagai base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    # 5 | return gambar base64
    return img_base64
