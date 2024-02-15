from PIL import Image as PILImage
from PIL import  ImageOps
from reportlab.lib.colors import Color
from qrcode import QRCode
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import numpy as np
import io

 

# QR kod oluşturmak için veri ve seri numarası kullanarak bir fonksiyon tanımlanıyor.
def create_qr_code_with_serial(data, serial):
    # QRCode sınıfından bir örnek oluşturuluyor.
    qr = QRCode(version=1)
    
    # QR koda veri ekleniyor.
    qr.add_data(data)
    
    # QR kodunun boyutunu otomatik olarak ayarlamak için make(fit=True) çağrılıyor.
    qr.make(fit=True)
    
    # Siyah renkte QR kodu oluştururken arka plan rengini beyaz olarak belirliyoruz.
    img = qr.make_image(fill='black', back_color='white')
    
    return img
# Resimleri ve etiketleri PDF belgesine yerleştiren fonksiyon tanımlanıyor
def add_images_to_pdf_with_label_grid_big_small(images_big, images_small, data_big, data_small, size_big, size_small, serial_numbers, pdf_path, label_text):
    # PDF belgesi oluşturuluyor
    doc = SimpleDocTemplate(pdf_path, pagesize=(pdf_width*inch, pdf_height*inch))
    
    # Stil örnekleri alınıyor
    styles = getSampleStyleSheet()

    # Metin stilini güncelleme
    body_text_style = styles['BodyText']
    body_text_style.fontName = 'Helvetica'
    body_text_style.fontSize = 8

    # Etiket metin stilini oluşturma
    label_style = styles['Normal']
    label_style.fontName = 'Helvetica'
    label_style.fontSize = 8

    # Boş resim listesi oluşturuluyor
    rl_images = []
    
    # Mevcut satır listesi oluşturuluyor
    current_row = []
    
    # Etiket genişliği hesaplanıyor
    label_width = (pdf_width - size_big * num_columns) / num_columns
    
    # Küçük QR kod tablosu oluşturma fonksiyonu tanımlanıyor
    def create_small_qr_table(rl_image_small, label_text, serial):
        # Küçük QR kod tablosu içeriği oluşturuluyor
        small_qr_table = Table([
            [rl_image_small],
            [Spacer(0, 0.1*inch)],
            [Paragraph(f"<font size=8>{label_text}<br/>SN: {serial}</font>", label_style)]
        ]) 
        small_qr_table.hAlign = 'LEFT'
        small_qr_table.spaceBefore = 0
        small_qr_table.spaceAfter = 0

        # Tablo içeriği için veriler oluşturuluyor
        data = [[rl_image_small, Paragraph(f"<font size=7>{label_text}<br/>SN: {serial}</font>", label_style)]]
        
        # Tablo oluşturuluyor ve özellikleri belirleniyor
        small_qr_table = Table(data, colWidths=[0.4 * inch, 1.5*inch])
        small_qr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
            ('BOX', (0, 0), (-1, 0), 0.25, Color(200 / 255, 162 / 255, 200 / 255)),  # Lila rengi (RGB: 200, 162, 200)
            ('LEFTPADDING', (0, 0), (-1, -1), 0.3),
        ]))

        return small_qr_table

    # Resimleri döngü içinde işleme koyma
    for i, (image_big, image_small, data_big, data_small) in enumerate(zip(images_big, images_small, data_big, data_small)):
        # Büyük ve küçük resimler numpy dizisine dönüştürülüyor
        image_np_big = np.array(image_big)
        image_np_small = np.array(image_small)
        
        # Resimler byte dizilerine dönüştürülüyor
        image_bytes_big = io.BytesIO()
        image_bytes_small = io.BytesIO() 
        PILImage.fromarray(image_np_big).save(image_bytes_big, format='PNG')
        PILImage.fromarray(image_np_small).save(image_bytes_small, format='PNG')
        
        # ReportLabImage öğeleri oluşturuluyor
        rl_image_big = ReportLabImage(image_bytes_big, width=size_big*inch, height=size_big*inch)
        rl_image_small = ReportLabImage(image_bytes_small, width=size_small*inch, height=size_small*inch)
 
        # Seri numarası alınıyor
        serial = serial_numbers.pop(0)

        # Büyük resim için tablo oluşturuluyor
        img_table = Table([
            [rl_image_big],
        ], colWidths=0.9*inch, rowHeights=0.9*inch)

        # Büyük resim tablosunun çerçeve stili belirleniyor
        qr_img_table_frame_style = TableStyle([
            ('BOX', (0, 0), (0, 0), 0.25, Color(200 / 255, 162 / 255, 200 / 255)),  # Lila rengi (RGB: 200, 162, 200)
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),    
        ])
        
        # Tabloya çerçeve stili uygulanıyor
        img_table.setStyle(qr_img_table_frame_style)

        # Büyük QR kod tablosu oluşturuluyor
        big_qr_table = Table([
            [img_table],
            [create_small_qr_table(rl_image_small, label_text, serial)]
        ])
        
        # Büyük QR kod tablosunun çerçeve stili belirleniyor
        qr_frame_style = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white), 
            ('BOX', (0, 0), (-1, -1), 0.1, colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1 * inch),  # Hücrelerin altına boşluk ekleme  
        ])

        # Tabloya çerçeve stili uygulanıyor
        big_qr_table.setStyle(qr_frame_style)


        # Büyük QR kod tablosu mevcut satıra ekleniyor
        current_row.append(big_qr_table)

        # Belirli bir sütun sayısına ulaşıldığında
        if (i + 1) % num_columns == 0:
            # Mevcut satırdaki tabloyu birleştirerek yeni bir tablo oluşturuluyor
            table = Table([current_row], colWidths=[pdf_width*inch/num_columns]*num_columns)
            table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.white),
                ('BOX', (0,0), (-1,-1), 0.25, colors.white),
            ]))
            
            # Oluşturulan tablo mevcut PDF resimler listesine ekleniyor
            rl_images.append(table)
            
            # Mevcut satır sıfırlanıyor
            current_row = []

    # PDF belgesi oluşturuluyor
    doc.build(rl_images)

# Seri numaralarını dosyadan okuyan fonksiyon tanımlanıyor
def read_serial_numbers(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Dosya yolları belirleniyor
file_path_tags = "DIY_Tags.txt"
file_path_cards = "DIY_Cards.txt"

# Seri numaraları okunuyor
serial_numbers_tags = read_serial_numbers(file_path_tags)
serial_numbers_cards = read_serial_numbers(file_path_cards)

# Etiket listeleri oluşturuluyor
diy_tags = [f"DIY-Tags-{serial}" for serial in serial_numbers_tags]
diy_cards = [f"DIY-Cards-{serial}" for serial in serial_numbers_cards]

# QR kod resimleri oluşturuluyor
qr_images_tags_big =[create_qr_code_with_serial(data, serial) for data, serial in zip(diy_tags, serial_numbers_tags)]
qr_images_cards_small = [create_qr_code_with_serial(data, serial) for data, serial in zip(diy_cards, serial_numbers_cards)]

# PDF boyutları ve sütun sayısı belirleniyor
big_qr_size = 0.999
small_qr_size = 0.375
pdf_width = 13
pdf_height = 15.999
num_columns = 5

# PDF dosya yolları belirleniyor
pdf_path_tags = "QR_Codes_Tags.pdf"
pdf_path_cards = "QR_Codes_Cards.pdf"

# DIY Talkido Cards PDF oluşturuluyor
etiket_metni_kartlar = "DIY Talkido Cards"
add_images_to_pdf_with_label_grid_big_small(qr_images_cards_small, qr_images_cards_small, diy_cards, diy_cards, big_qr_size, small_qr_size, serial_numbers_cards.copy(), pdf_path_cards, etiket_metni_kartlar)

# DIY Talkido Tags PDF oluşturuluyor
etiket_metni_etiketler = "DIY Talkido Tags"
add_images_to_pdf_with_label_grid_big_small(qr_images_tags_big, qr_images_tags_big, diy_tags, diy_tags, big_qr_size, small_qr_size, serial_numbers_tags.copy(), pdf_path_tags, etiket_metni_etiketler)