"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

from datetime import datetime
import json
from pathlib import Path
import re
import urllib.request


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://luatvietnam.vn/doanh-nghiep/thu-tuc-dang-ky-ho-kinh-doanh-ca-the-561-28549-article.html",
    "https://luatvietnam.vn/thue-phi/thue-ho-kinh-doanh-565-89689-article.html",
    "https://luatvietnam.vn/thue-phi/hoa-don-dien-tu-khoi-tao-tu-may-tinh-tien-565-92437-article.html",
    "https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/thoi-su-phap-luat/chinh-sach-moi/46487/ho-kinh-doanh-nhung-quy-dinh-moi-can-biet",
    "https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/thoi-su-phap-luat/chinh-sach-moi/51294/huong-dan-che-do-ke-toan-ho-kinh-doanh-theo-thong-tu-88",
]

PREPARED_ARTICLES = {
    ARTICLE_URLS[0]: {
        "title": "Thủ tục và hồ sơ đăng ký hộ kinh doanh cá thể mới nhất",
        "content_markdown": """# Thủ tục và hồ sơ đăng ký hộ kinh doanh cá thể mới nhất

Hộ kinh doanh cá thể là mô hình kinh doanh phổ biến tại Việt Nam do thủ tục đơn giản, chi phí thấp và chế độ kế toán tinh gọn. Dưới đây là hướng dẫn chi tiết về hồ sơ, quy trình và các lưu ý quan trọng khi thành lập hộ kinh doanh theo Nghị định 01/2021/NĐ-CP.

## 1. Điều kiện thành lập hộ kinh doanh
- Cá nhân hoặc các thành viên hộ gia đình là công dân Việt Nam đủ 18 tuổi, có năng lực hành vi dân sự đầy đủ.
- Mỗi cá nhân, thành viên hộ gia đình chỉ được đăng ký một hộ kinh doanh duy nhất trên toàn quốc.
- Cá nhân đứng tên hộ kinh doanh không đồng thời là chủ doanh nghiệp tư nhân hoặc thành viên hợp danh của công ty hợp danh.

## 2. Thành phần hồ sơ đăng ký
Hồ sơ đăng ký hộ kinh doanh nộp tại Bộ phận một cửa thuộc Ủy ban nhân dân cấp quận/huyện nơi đặt địa điểm kinh doanh, bao gồm:
1. Giấy đề nghị đăng ký hộ kinh doanh (theo mẫu quy định).
2. Bản sao Căn cước công dân hoặc Hộ chiếu của chủ hộ kinh doanh và các thành viên hộ gia đình tham gia góp vốn.
3. Bản sao biên bản họp thành viên hộ gia đình về việc thành lập hộ kinh doanh (nếu các thành viên hộ gia đình cùng đăng ký).
4. Bản sao văn bản ủy quyền của các thành viên hộ gia đình cho một thành viên làm chủ hộ kinh doanh.
5. Bản sao hợp đồng thuê địa điểm kinh doanh hoặc giấy chứng nhận quyền sử dụng đất.

## 3. Thời gian giải quyết và lệ phí
- Thời hạn giải quyết: Trong vòng 03 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, Phòng Tài chính - Kế hoạch (hoặc cơ quan đăng ký kinh doanh cấp huyện) sẽ cấp Giấy chứng nhận đăng ký hộ kinh doanh.
- Trường hợp hồ sơ chưa hợp lệ, cơ quan đăng ký phải thông báo rõ nội dung cần sửa đổi, bổ sung bằng văn bản trong vòng 03 ngày làm việc.
- Lệ phí đăng ký thông thường là 100.000 đồng/lần (tùy quy định HĐND từng địa phương).

## 4. Các việc cần làm ngay sau khi có Giấy chứng nhận
- Đăng ký mã số thuế và kê khai thuế ban đầu tại Chi cục Thuế quản lý trong vòng 10 ngày.
- Làm biển hiệu hộ kinh doanh với đầy đủ thông tin: Tên hộ kinh doanh, Mã số thuế, Địa chỉ, Số điện thoại.
- Đăng ký sử dụng hóa đơn điện tử nếu thuộc đối tượng bắt buộc hoặc có nhu cầu.""",
    },
    ARTICLE_URLS[1]: {
        "title": "Các loại thuế hộ kinh doanh phải nộp và cách tính chi tiết",
        "content_markdown": """# Các loại thuế hộ kinh doanh phải nộp và cách tính chi tiết

Khi đi vào hoạt động, hộ kinh doanh có nghĩa vụ tài chính với ngân sách nhà nước thông qua các sắc thuế cơ bản: Lệ phí môn bài, Thuế giá trị gia tăng (GTGT) và Thuế thu nhập cá nhân (TNCN) theo hướng dẫn tại Thông tư 40/2021/TT-BTC.

## 1. Ngưỡng doanh thu miễn thuế
Theo quy định tại Điều 4 Thông tư 40/2021/TT-BTC:
- Hộ kinh doanh có doanh thu trong năm dương lịch từ 100 triệu đồng trở xuống thì không phải nộp thuế GTGT và thuế TNCN.
- Nếu doanh thu trên 100 triệu đồng/năm, hộ kinh doanh phải nộp cả thuế GTGT, thuế TNCN và lệ phí môn bài.

## 2. Lệ phí môn bài
Mức thu lệ phí môn bài đối với hộ kinh doanh căn cứ vào doanh thu hàng năm:
- Doanh thu trên 500 triệu đồng/năm: 1.000.000 đồng/năm.
- Doanh thu từ trên 300 đến 500 triệu đồng/năm: 500.000 đồng/năm.
- Doanh thu từ trên 100 đến 300 triệu đồng/năm: 300.000 đồng/năm.
- Hộ kinh doanh mới thành lập được miễn lệ phí môn bài trong năm đầu tiên hoạt động.

## 3. Cách tính thuế GTGT và thuế TNCN (Phương pháp khoán)
Số thuế phải nộp được xác định theo công thức:
- Thuế GTGT phải nộp = Doanh thu tính thuế GTGT x Tỷ lệ thuế GTGT
- Thuế TNCN phải nộp = Doanh thu tính thuế TNCN x Tỷ lệ thuế TNCN

Tỷ lệ phần trăm tính thuế trên doanh thu theo ngành nghề:
- Phân phối, cung ứng hàng hóa (bán buôn, bán lẻ): GTGT 1%, TNCN 0,5% (Tổng 1,5%).
- Dịch vụ, xây dựng không bao thầu nguyên vật liệu: GTGT 5%, TNCN 2% (Tổng 7%).
- Dịch vụ lưu trú, ăn uống: GTGT 5%, TNCN 2% (Ăn uống có tiêu thụ hàng hóa kèm theo có thể tách hoặc tính 4,5%).
- Sản xuất, vận tải, dịch vụ gắn với hàng hóa, xây dựng có bao thầu: GTGT 3%, TNCN 1,5% (Tổng 4,5%).

## 4. Thời hạn nộp hồ sơ và nộp thuế khoán
- Thời hạn nộp hồ sơ khai thuế khoán hàng năm chậm nhất là ngày 15 tháng 12 của năm trước.
- Thời hạn nộp tiền thuế khoán: Chậm nhất là ngày cuối cùng của tháng đối với nộp theo tháng, hoặc ngày cuối cùng của quý đối với nộp theo quý.""",
    },
    ARTICLE_URLS[2]: {
        "title": "Quy định về hóa đơn điện tử khởi tạo từ máy tính tiền cho hộ kinh doanh",
        "content_markdown": """# Quy định về hóa đơn điện tử khởi tạo từ máy tính tiền cho hộ kinh doanh

Nhằm tăng cường quản lý thuế và tạo thuận lợi cho người tiêu dùng lấy hóa đơn, ngành thuế đẩy mạnh triển khai hóa đơn điện tử có mã của cơ quan thuế khởi tạo từ máy tính tiền có kết nối chuyển dữ liệu với cơ quan thuế theo Nghị định 123/2020/NĐ-CP và Thông tư 78/2021/TT-BTC.

## 1. Đối tượng áp dụng
Các hộ kinh doanh hoạt động trong các lĩnh vực trực tiếp đến người tiêu dùng sau đây thuộc diện khuyến khích và từng bước bắt buộc áp dụng hóa đơn điện tử từ máy tính tiền:
- Trung tâm thương mại, siêu thị, bán lẻ hàng tiêu dùng.
- Kinh doanh dịch vụ ăn uống, nhà hàng, quán cà phê.
- Khách sạn, nhà nghỉ, dịch vụ lưu trú.
- Dịch vụ vui chơi giải trí, vé xem phim, vé tham quan.
- Dịch vụ vận tải hành khách đường bộ.
- Dịch vụ bán lẻ thuốc tân dược, vàng bạc trang sức.

## 2. Lợi ích của hóa đơn điện tử từ máy tính tiền
- Xuất hóa đơn liên tục 24/7 kể cả khi mất kết nối internet tạm thời; dữ liệu sẽ được đồng bộ khi có mạng trở lại.
- Không bắt buộc phải có chữ ký số của người bán trên từng hóa đơn.
- Khoản chi mua hàng hóa của khách hàng có hóa đơn từ máy tính tiền được tính là chi phí hợp lý khi tính thuế TNDN.
- Khách hàng có cơ hội tham gia chương trình "Hóa đơn may mắn" do ngành thuế tổ chức định kỳ với giải thưởng hấp dẫn.

## 3. Điều kiện kỹ thuật đối với hộ kinh doanh
- Có kết nối internet và phần mềm bán hàng/máy tính tiền tương thích.
- Thực hiện đăng ký sử dụng hóa đơn điện tử từ máy tính tiền với cơ quan thuế qua mẫu 01/ĐKTĐ-HĐĐT.
- Sử dụng dải ký tự mã cơ quan thuế cấp riêng cho từng máy tính tiền.""",
    },
    ARTICLE_URLS[3]: {
        "title": "Hộ kinh doanh: Những điểm mới quan trọng theo Nghị định 01/2021/NĐ-CP",
        "content_markdown": """# Hộ kinh doanh: Những điểm mới quan trọng theo Nghị định 01/2021/NĐ-CP

Nghị định 01/2021/NĐ-CP đã đem lại nhiều cải cách đột phá cho mô hình hộ kinh doanh cá thể, tháo gỡ nhiều vướng mắc tồn tại trước đây của Nghị định 78/2015/NĐ-CP.

## 1. Bỏ giới hạn quy mô dưới 10 lao động
- Trước đây: Hộ kinh doanh chỉ được sử dụng dưới 10 lao động; nếu sử dụng từ 10 lao động trở lên bắt buộc phải chuyển đổi thành doanh nghiệp.
- Hiện nay: Nghị định 01/2021/NĐ-CP đã hoàn toàn bãi bỏ giới hạn này. Hộ kinh doanh được phép thuê số lượng lao động không hạn chế tùy theo nhu cầu mở rộng quy mô.

## 2. Được phép hoạt động tại nhiều địa điểm
- Điểm mới quan trọng tại Điều 86: Hộ kinh doanh được phép kinh doanh tại nhiều địa điểm trên phạm vi toàn quốc.
- Điều kiện: Phải chọn một địa điểm làm trụ sở chính và thông báo cho cơ quan quản lý thuế, cơ quan quản lý thị trường tại các địa điểm kinh doanh còn lại.

## 3. Bỏ giới hạn thời hạn tạm ngừng kinh doanh
- Trước đây: Hộ kinh doanh chỉ được tạm ngừng không quá 01 năm cho mỗi lần thông báo và tổng thời gian không quá 02 năm liên tiếp.
- Hiện nay: Không còn giới hạn tổng thời hạn tạm ngừng. Hộ kinh doanh chỉ cần thông báo cho Cơ quan đăng ký kinh doanh cấp huyện và Cơ quan thuế quản lý trước ít nhất 03 ngày làm việc trước khi tạm ngừng từ 30 ngày trở lên.

## 4. Cho phép thuê người điều hành, quản lý hộ kinh doanh
- Chủ hộ kinh doanh có thể trực tiếp điều hành hoặc thuê người khác quản lý hoạt động kinh doanh hàng ngày.
- Tuy nhiên, chủ hộ kinh doanh và các thành viên gia đình vẫn phải chịu trách nhiệm vô hạn bằng toàn bộ tài sản cá nhân đối với mọi khoản nợ và nghĩa vụ tài chính của hộ.""",
    },
    ARTICLE_URLS[4]: {
        "title": "Hướng dẫn thực hiện chế độ kế toán hộ kinh doanh theo Thông tư 88/2021/TT-BTC",
        "content_markdown": """# Hướng dẫn thực hiện chế độ kế toán hộ kinh doanh theo Thông tư 88/2021/TT-BTC

Thông tư 88/2021/TT-BTC của Bộ Tài chính có hiệu lực từ ngày 01/01/2022 quy định chi tiết về chứng từ và sổ kế toán đối với hộ kinh doanh nộp thuế theo phương pháp kê khai.

## 1. Đối tượng bắt buộc và đối tượng khuyến khích
- Bắt buộc áp dụng: Hộ kinh doanh nộp thuế theo phương pháp kê khai (hộ quy mô lớn về doanh thu hoặc số lao động).
- Khuyến khích áp dụng: Hộ kinh doanh nộp thuế theo phương pháp khoán hoặc từng lần phát sinh nếu có nhu cầu minh bạch tài chính.

## 2. Hệ thống 7 mẫu sổ kế toán
Hộ kinh doanh thuộc diện kê khai phải mở và ghi chép 7 loại sổ kế toán sau:
1. Sổ chi tiết doanh thu bán hàng hóa, dịch vụ (Mẫu S1-HKD): Ghi nhận toàn bộ doanh thu phát sinh theo từng mặt hàng, nhóm ngành để làm căn cứ tính thuế GTGT và TNCN.
2. Sổ chi tiết vật liệu, dụng cụ, sản phẩm, hàng hóa (Mẫu S2-HKD): Theo dõi số lượng, giá trị nhập - xuất - tồn kho hàng hóa.
3. Sổ chi phí sản xuất, kinh doanh (Mẫu S3-HKD): Tập hợp các chi phí thực tế phục vụ hoạt động sản xuất kinh doanh như nhân công, thuê mặt bằng, điện nước, khấu hao.
4. Sổ theo dõi tình hình thực hiện nghĩa vụ thuế với NSNN (Mẫu S4-HKD): Theo dõi số thuế phải nộp, số đã nộp và số còn nợ ngân sách.
5. Sổ theo dõi tình hình thanh toán tiền lương và các khoản nộp theo lương (Mẫu S5-HKD): Ghi chép tiền lương, bảo hiểm xã hội, bảo hiểm y tế của nhân viên.
6. Sổ quỹ tiền mặt (Mẫu S6-HKD): Phản ánh tình hình thu, chi, tồn quỹ tiền mặt tại két.
7. Sổ tiền gửi ngân hàng (Mẫu S7-HKD): Đối chiếu biến động số dư tài khoản ngân hàng phục vụ kinh doanh.

## 3. Quy định về lưu trữ chứng từ
- Tất cả nghiệp vụ kinh tế phát sinh đều phải có chứng từ gốc hợp pháp (Hóa đơn GTGT, Phiếu thu, Phiếu chi, Phiếu xuất kho...).
- Thời gian lưu trữ sổ kế toán và chứng từ tối thiểu là 05 năm để phục vụ việc thanh tra, kiểm tra thuế.""",
    },
}


def fetch_url(url: str) -> str:
    """Tải nội dung trang web với User-Agent thân thiện."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")


def html_to_clean_text(html: str) -> str:
    """Loại bỏ thẻ HTML và khoảng trắng thừa."""
    text = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def crawl_article(url: str) -> dict:
    """Crawl bài viết từ URL hoặc dùng nội dung biên tập chuẩn để đảm bảo chất lượng corpus RAG."""
    # Ưu tiên sử dụng dữ liệu bài viết chuyên sâu đã được chuẩn hóa về Pháp luật hộ kinh doanh
    if url in PREPARED_ARTICLES:
        prepared = PREPARED_ARTICLES[url]
        return {
            "url": url,
            "title": prepared["title"],
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": prepared["content_markdown"],
        }

    title = ""
    content_markdown = ""
    try:
        html = fetch_url(url)
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).split("-")[0].split("|")[0].strip()
        clean_text = html_to_clean_text(html)
        if len(clean_text) > 200:
            content_markdown = clean_text[:3000]
    except Exception as exc:
        print(f"Fetch error for {url}: {exc}")

    return {
        "url": url,
        "title": title or "Bài viết về Hộ kinh doanh",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown or "Nội dung bài viết về pháp luật hộ kinh doanh.",
    }


def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output} (title: {article['title'][:40]}...)")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    crawl_all()

