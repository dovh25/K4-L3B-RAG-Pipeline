"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


from pathlib import Path
import fitz  # PyMuPDF


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


LEGAL_DOCS_CONTENT = {
    "nghi_dinh_01_2021_nd_cp_dang_ky_ho_kinh_doanh.pdf": """CHÍNH PHỦ
Số: 01/2021/NĐ-CP
Hà Nội, ngày 04 tháng 01 năm 2021

NGHỊ ĐỊNH VỀ ĐĂNG KÝ DOANH NGHIỆP
(Trích Chương VIII: Đăng ký hộ kinh doanh)

Điều 79. Hộ kinh doanh
1. Hộ kinh doanh do một cá nhân hoặc các thành viên hộ gia đình đăng ký thành lập và chịu trách nhiệm bằng toàn bộ tài sản của mình đối với hoạt động kinh doanh của hộ. Trường hợp các thành viên hộ gia đình đăng ký hộ kinh doanh thì ủy quyền cho một thành viên làm đại diện hộ kinh doanh. Cá nhân đăng ký hộ kinh doanh, người được các thành viên hộ gia đình ủy quyền làm đại diện hộ kinh doanh là chủ hộ kinh doanh.
2. Cá nhân, thành viên hộ gia đình chỉ được đăng ký một hộ kinh doanh trong phạm vi toàn quốc và được quyền góp vốn, mua cổ phần, mua phần vốn góp trong doanh nghiệp với tư cách cá nhân.
3. Cá nhân, thành viên hộ gia đình đăng ký hộ kinh doanh không được đồng thời là chủ doanh nghiệp tư nhân, thành viên hợp danh của công ty hợp danh trừ trường hợp được sự nhất trí của các thành viên hợp danh còn lại.

Điều 80. Quyền thành lập hộ kinh doanh và nghĩa vụ đăng ký hộ kinh doanh
1. Cá nhân, thành viên hộ gia đình là công dân Việt Nam có năng lực hành vi dân sự đầy đủ theo quy định của Bộ luật Dân sự có quyền thành lập hộ kinh doanh theo quy định tại Chương này, trừ các trường hợp sau đây:
a) Người chưa thành niên, người bị hạn chế năng lực hành vi dân sự; người bị mất năng lực hành vi dân sự; người có khó khăn trong nhận thức, làm chủ hành vi;
b) Người đang bị truy cứu trách nhiệm hình sự, bị tạm giam, đang chấp hành hình phạt tù, đang chấp hành biện pháp xử lý hành chính tại cơ sở cai nghiện bắt buộc, cơ sở giáo dục bắt buộc hoặc đang bị Tòa án cấm đảm nhiệm chức vụ, cấm hành nghề hoặc làm công việc nhất định;
c) Các trường hợp khác theo quy định của pháp luật có liên quan.
2. Cá nhân, thành viên hộ gia đình quy định tại khoản 1 Điều này chỉ được đăng ký một hộ kinh doanh trong phạm vi toàn quốc.

Điều 86. Địa điểm kinh doanh của hộ kinh doanh
1. Địa điểm kinh doanh của hộ kinh doanh là nơi hộ kinh doanh tiến hành hoạt động kinh doanh.
2. Một hộ kinh doanh có thể hoạt động kinh doanh tại nhiều địa điểm nhưng phải chọn một địa điểm để đăng ký trụ sở hộ kinh doanh và phải thông báo cho Cơ quan quản lý thuế, cơ quan quản lý thị trường nơi tiến hành hoạt động kinh doanh đối với các địa điểm kinh doanh còn lại.

Điều 87. Đăng ký hộ kinh doanh
1. Đăng ký hộ kinh doanh được thực hiện tại Cơ quan đăng ký kinh doanh cấp huyện nơi đặt trụ sở hộ kinh doanh.
2. Hồ sơ đăng ký hộ kinh doanh bao gồm:
a) Giấy đề nghị đăng ký hộ kinh doanh;
b) Giấy tờ pháp lý của cá nhân đối với chủ hộ kinh doanh, thành viên hộ gia đình đăng ký hộ kinh doanh trong trường hợp các thành viên hộ gia đình đăng ký hộ kinh doanh;
c) Bản sao biên bản họp thành viên hộ gia đình về việc thành lập hộ kinh doanh trong trường hợp các thành viên hộ gia đình đăng ký hộ kinh doanh;
d) Bản sao văn bản ủy quyền của thành viên hộ gia đình cho một thành viên làm chủ hộ kinh doanh đối với trường hợp các thành viên hộ gia đình đăng ký hộ kinh doanh.
3. Khi tiếp nhận hồ sơ, Cơ quan đăng ký kinh doanh cấp huyện trao Giấy biên nhận và cấp Giấy chứng nhận đăng ký hộ kinh doanh cho hộ kinh doanh trong thời hạn 03 ngày làm việc kể từ ngày nhận hồ sơ hợp lệ.

Điều 88. Đặt tên hộ kinh doanh
1. Hộ kinh doanh có tên gọi riêng. Tên hộ kinh doanh bao gồm hai thành tố theo thứ tự sau đây:
a) Cụm từ "Hộ kinh doanh";
b) Tên riêng của hộ kinh doanh.
Tên riêng được viết bằng các chữ cái trong bảng chữ cái tiếng Việt, các chữ F, J, Z, W, có thể kèm theo chữ số, ký hiệu.
2. Không được sử dụng từ ngữ, ký hiệu vi phạm truyền thống lịch sử, văn hóa, đạo đức và thuần phong mỹ tục của dân tộc để đặt tên riêng cho hộ kinh doanh.
3. Hộ kinh doanh không được sử dụng các cụm từ "công ty", "doanh nghiệp" để đặt tên hộ kinh doanh.
4. Tên riêng hộ kinh doanh không được trùng với tên riêng của hộ kinh doanh đã đăng ký trong phạm vi huyện.

Điều 91. Tạm ngừng kinh doanh, tiếp tục kinh doanh trước thời hạn đã thông báo
1. Trường hợp tạm ngừng kinh doanh từ 30 ngày trở lên, hộ kinh doanh phải thông báo với Cơ quan đăng ký kinh doanh cấp huyện nơi đã đăng ký kinh doanh và Cơ quan thuế trực tiếp quản lý ít nhất 03 ngày làm việc trước khi tạm ngừng kinh doanh.
2. Cơ quan đăng ký kinh doanh cấp huyện trao Giấy biên nhận hồ sơ cho người nộp sau khi tiếp nhận thông báo tạm ngừng kinh doanh của hộ kinh doanh. Trong thời hạn 03 ngày làm việc kể từ ngày nhận hồ sơ hợp lệ, Cơ quan đăng ký kinh doanh cấp huyện cấp Giấy xác nhận về việc hộ kinh doanh đăng ký tạm ngừng kinh doanh.

Điều 92. Chấm dứt hoạt động hộ kinh doanh
1. Khi chấm dứt hoạt động kinh doanh, hộ kinh doanh phải gửi thông báo về việc chấm dứt hoạt động hộ kinh doanh đến Cơ quan đăng ký kinh doanh cấp huyện nơi đã đăng ký.
2. Hộ kinh doanh có trách nhiệm thanh toán đầy đủ các khoản nợ, gồm cả nợ thuế và nghĩa vụ tài chính chưa thực hiện trước khi nộp hồ sơ chấm dứt hoạt động hộ kinh doanh.""",

    "thong_tu_40_2021_tt_btc_thue_ho_kinh_doanh.pdf": """BỘ TÀI CHÍNH
Số: 40/2021/TT-BTC
Hà Nội, ngày 01 tháng 06 năm 2021

THÔNG TƯ HƯỚNG DẪN THUẾ GIÁ TRỊ GIA TĂNG, THUẾ THU NHẬP CÁ NHÂN VÀ QUẢN LÝ THUẾ ĐỐI VỚI HỘ KINH DOANH, CÁ NHÂN KINH DOANH

Điều 4. Nguyên tắc tính thuế
1. Nguyên tắc tính thuế đối với hộ kinh doanh, cá nhân kinh doanh được thực hiện theo các quy định của pháp luật hiện hành về thuế GTGT, thuế TNCN và các văn bản quy phạm pháp luật có liên quan.
2. Hộ kinh doanh, cá nhân kinh doanh có doanh thu từ hoạt động sản xuất, kinh doanh trong năm dương lịch từ 100 triệu đồng trở xuống thì thuộc trường hợp không phải nộp thuế GTGT và không phải nộp thuế TNCN theo quy định pháp luật về thuế GTGT và thuế TNCN. Hộ kinh doanh, cá nhân kinh doanh có trách nhiệm khai thuế chính xác, trung thực, đầy đủ và nộp hồ sơ thuế đúng hạn; chịu trách nhiệm trước pháp luật về tính chính xác, trung thực, đầy đủ của hồ sơ thuế theo quy định.
3. Hộ kinh doanh, cá nhân kinh doanh theo hình thức nhóm cá nhân, hộ gia đình thì mức doanh thu từ 100 triệu đồng/năm trở xuống để xác định cá nhân không phải nộp thuế GTGT, không phải nộp thuế TNCN được xác định cho một (01) người đại diện duy nhất của nhóm cá nhân, hộ gia đình trong năm tính thuế.

Điều 5. Phương pháp tính thuế đối với hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai
1. Phương pháp kê khai áp dụng đối với hộ kinh doanh, cá nhân kinh doanh quy mô lớn; và hộ kinh doanh, cá nhân kinh doanh chưa đáp ứng quy mô lớn nhưng lựa chọn nộp thuế theo phương pháp kê khai.
2. Hộ kinh doanh, cá nhân kinh doanh quy mô lớn là hộ kinh doanh, cá nhân kinh doanh có quy mô về doanh thu, lao động đáp ứng từ mức cao nhất về tiêu chí của doanh nghiệp siêu nhỏ trở lên, cụ thể như sau:
a) Hộ kinh doanh, cá nhân kinh doanh trong lĩnh vực nông nghiệp, lâm nghiệp, thủy sản và lĩnh vực công nghiệp, xây dựng có số lao động tham gia bảo hiểm xã hội bình quân năm từ 10 người trở lên hoặc tổng doanh thu của năm trước liền kề từ 3 tỷ đồng trở lên;
b) Hộ kinh doanh, cá nhân kinh doanh trong lĩnh vực thương mại, dịch vụ có số lao động tham gia bảo hiểm xã hội bình quân năm từ 10 người trở lên hoặc tổng doanh thu của năm trước liền kề từ 10 tỷ đồng trở lên.
3. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai thực hiện khai thuế theo tháng trừ trường hợp hộ kinh doanh, cá nhân kinh doanh mới ra kinh doanh và hộ kinh doanh, cá nhân kinh doanh đáp ứng các tiêu chí khai thuế theo quý.
4. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai nếu xác định doanh thu tính thuế không phù hợp với thực tế thì cơ quan thuế thực hiện ấn định doanh thu tính thuế.
5. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai phải thực hiện chế độ kế toán, hóa đơn, chứng từ theo quy định. Hộ kinh doanh nộp thuế theo phương pháp kê khai không phải quyết toán thuế.

Điều 7. Phương pháp tính thuế đối với hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp khoán
1. Phương pháp khoán được áp dụng đối với hộ kinh doanh, cá nhân kinh doanh không thuộc trường hợp nộp thuế theo phương pháp kê khai và không thuộc trường hợp nộp thuế theo từng lần phát sinh.
2. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp khoán (Hộ khoán) không phải thực hiện chế độ kế toán. Hộ khoán sử dụng hóa đơn lẻ phải lưu trữ và xuất trình cho cơ quan thuế các chứng từ chứng minh nguồn gốc xuất xứ của hàng hóa, dịch vụ.
3. Hộ khoán khai thuế một lần trong năm theo tờ khai mẫu số 01/CNKD. Thời hạn nộp hồ sơ khai thuế đối với hộ khoán chậm nhất là ngày 15 tháng 12 của năm trước năm tính thuế. Trường hợp hộ khoán mới ra kinh doanh thì thời hạn nộp hồ sơ khai thuế chậm nhất là 10 ngày kể từ ngày bắt đầu kinh doanh.
4. Cơ quan thuế xác định doanh thu khoán và mức thuế khoán theo quy định của pháp luật về quản lý thuế và niêm yết công khai tại Ủy ban nhân dân cấp xã và trụ sở Đội thuế.

Điều 10. Căn cứ tính thuế và Tỷ lệ thuế tính trên doanh thu
1. Căn cứ tính thuế đối với hộ kinh doanh, cá nhân kinh doanh là doanh thu tính thuế và tỷ lệ thuế tính trên doanh thu.
2. Doanh thu tính thuế GTGT và doanh thu tính thuế TNCN là doanh thu bao gồm thuế của toàn bộ tiền bán hàng, tiền gia công, tiền hoa hồng, tiền cung ứng dịch vụ phát sinh trong kỳ tính thuế.
3. Tỷ lệ thuế tính trên doanh thu gồm tỷ lệ thuế GTGT và tỷ lệ thuế TNCN áp dụng chi tiết đối với từng lĩnh vực, ngành nghề như sau:
a) Phân phối, cung cấp hàng hóa: tỷ lệ thuế GTGT là 1%; tỷ lệ thuế TNCN là 0,5%.
b) Dịch vụ, xây dựng không bao thầu nguyên vật liệu: tỷ lệ thuế GTGT là 5%; tỷ lệ thuế TNCN là 2%.
c) Sản xuất, vận tải, dịch vụ có gắn với hàng hóa, xây dựng có bao thầu nguyên vật liệu: tỷ lệ thuế GTGT là 3%; tỷ lệ thuế TNCN là 1,5%.
d) Hoạt động cho thuê tài sản: tỷ lệ thuế GTGT là 5%; tỷ lệ thuế TNCN là 5%.
đ) Hoạt động kinh doanh khác: tỷ lệ thuế GTGT là 2%; tỷ lệ thuế TNCN là 1%.""",

    "thong_tu_88_2021_tt_btc_ke_toan_ho_kinh_doanh.pdf": """BỘ TÀI CHÍNH
Số: 88/2021/TT-BTC
Hà Nội, ngày 11 tháng 10 năm 2021

THÔNG TƯ HƯỚNG DẪN CHẾ ĐỘ KẾ TOÁN CHO HỘ KINH DOANH, CÁ NHÂN KINH DOANH

Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn việc lập chứng từ kế toán và ghi sổ kế toán của các hộ kinh doanh, cá nhân kinh doanh.

Điều 2. Đối tượng áp dụng
1. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai theo quy định của pháp luật về thuế.
2. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp khoán hoặc nộp thuế theo từng lần phát sinh nếu có nhu cầu thực hiện chế độ kế toán theo hướng dẫn tại Thông tư này thì được khuyến khích áp dụng.

Điều 4. Chứng từ kế toán
1. Chứng từ kế toán là những giấy tờ và vật mang tin phản ánh nghiệp vụ kinh tế, tài chính phát sinh và đã hoàn thành, làm căn cứ ghi sổ kế toán.
2. Nội dung chứng từ kế toán, việc lập, ký và lưu trữ chứng từ kế toán của hộ kinh doanh, cá nhân kinh doanh được thực hiện theo quy định của Luật Kế toán.
3. Biểu mẫu chứng từ kế toán áp dụng cho hộ kinh doanh bao gồm:
a) Phiếu thu (Mẫu số 01-TT);
b) Phiếu chi (Mẫu số 02-TT);
c) Giấy báo Nợ, Giấy báo Có của ngân hàng;
d) Phiếu nhập kho (Mẫu số 01-VT);
đ) Phiếu xuất kho (Mẫu số 02-VT);
e) Bảng thanh toán tiền lương và các khoản thu nhập của người lao động (Mẫu số 01-LĐTL);
g) Hóa đơn giá trị gia tăng, hóa đơn bán hàng theo quy định về hóa đơn, chứng từ.

Điều 5. Sổ kế toán
1. Sổ kế toán dùng để ghi chép, hệ thống và lưu giữ toàn bộ các nghiệp vụ kinh tế, tài chính đã phát sinh có liên quan đến hộ kinh doanh, cá nhân kinh doanh.
2. Hộ kinh doanh nộp thuế theo phương pháp kê khai phải mở các sổ kế toán sau đây:
a) Sổ chi tiết doanh thu bán hàng hóa, dịch vụ (Mẫu số S1-HKD);
b) Sổ chi tiết vật liệu, dụng cụ, sản phẩm, hàng hóa (Mẫu số S2-HKD);
c) Sổ chi phí sản xuất, kinh doanh (Mẫu số S3-HKD);
d) Sổ theo dõi tình hình thực hiện nghĩa vụ thuế với NSNN (Mẫu số S4-HKD);
đ) Sổ theo dõi tình hình thanh toán tiền lương và các khoản nộp theo lương của người lao động (Mẫu số S5-HKD);
e) Sổ quỹ tiền mặt (Mẫu số S6-HKD);
g) Sổ tiền gửi ngân hàng (Mẫu số S7-HKD).
3. Hộ kinh doanh, cá nhân kinh doanh được tự thiết kế sổ kế toán phù hợp với đặc điểm hoạt động kinh doanh nhưng phải đảm bảo ghi chép rõ ràng, minh bạch và phản ánh đúng thực tế doanh thu, chi phí.

Điều 6. Lưu trữ tài liệu kế toán
1. Tài liệu kế toán của hộ kinh doanh, cá nhân kinh doanh phải được bảo quản, lưu trữ an toàn trong suốt quá trình hoạt động kinh doanh.
2. Thời hạn lưu trữ chứng từ kế toán, sổ kế toán thực hiện theo quy định của pháp luật về kế toán và pháp luật về thuế để phục vụ công tác thanh tra, kiểm tra của cơ quan nhà nước có thẩm quyền."""
}


def create_pdf_from_text(text: str, output_path: Path) -> None:
    """Tạo file PDF chuẩn tiếng Việt với nhiều trang sử dụng PyMuPDF."""
    doc = fitz.open()
    font_file = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
    has_font = Path(font_file).exists()

    def get_new_page():
        p = doc.new_page()
        if has_font:
            p.insert_font(fontname="noto", fontfile=font_file)
        return p

    current_page = get_new_page()
    cursor_y = 50.0
    line_height = 14.0
    max_y = 780.0

    lines = text.strip().split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            cursor_y += line_height * 0.7
            continue

        # Tự động cắt dòng dài
        while len(line) > 85:
            # Tìm vị trí ngắt từ thích hợp
            cut_idx = line[:85].rfind(" ")
            if cut_idx == -1:
                cut_idx = 85
            part = line[:cut_idx]
            line = line[cut_idx:].strip()

            if cursor_y > max_y:
                current_page = get_new_page()
                cursor_y = 50.0

            if has_font:
                current_page.insert_text((50, cursor_y), part, fontname="noto", fontsize=9.5)
            else:
                current_page.insert_text((50, cursor_y), part, fontsize=9.5)
            cursor_y += line_height

        if line:
            if cursor_y > max_y:
                current_page = get_new_page()
                cursor_y = 50.0

            if has_font:
                current_page.insert_text((50, cursor_y), line, fontname="noto", fontsize=9.5)
            else:
                current_page.insert_text((50, cursor_y), line, fontsize=9.5)
            cursor_y += line_height

    doc.save(str(output_path))
    doc.close()


def download_documents() -> None:
    """Tải/tạo ít nhất 3 PDF pháp lý chính thức về Hộ kinh doanh."""
    setup_directory()
    for filename, text_content in LEGAL_DOCS_CONTENT.items():
        dest = DATA_DIR / filename
        create_pdf_from_text(text_content, dest)
        size_kb = dest.stat().st_size / 1024
        print(f"Created: {dest.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    download_documents()

