from stop_words import get_stop_words
import re

vietnamese_stopwords = set(get_stop_words("vietnamese"))

def remove_stopwords(text: str) -> str:
    words = re.findall(r'\w+', text.lower(), flags=re.UNICODE)

    filtered_words = [w for w in words if w not in vietnamese_stopwords]

    return " ".join(filtered_words)

if __name__ == "__main__":
    content = """Ngày Quốc khánh 2/9 luôn là dịp đặc biệt để mỗi người Việt Nam cùng nhìn lại chặng đường lịch sử vẻ vang, nhắc nhớ về niềm tự hào dân tộc. Trong không khí rộn ràng ấy, hình ảnh những chiếc áo đỏ xuất hiện trên khắp các tuyến phố không chỉ tạo nên sắc màu rực rỡ, mà còn gợi nhắc đến tinh thần tự do, kiêu hãnh và sự gắn kết của cả dân tộc Việt Nam. Nhân dịp này, GOYA giới thiệu mẫu áo mới 2/9 - thiết kế mang đậm tinh thần dân tộc, để bạn vừa tự hào, vừa phong cách trong ngày lễ trọng đại. Khoác lên mình chiếc áo đỏ trong ngày lễ 2/9 không chỉ là sự lựa chọn trang phục. Đó còn là cách để bạn hòa mình vào dòng người hân hoan kỷ niệm, để sắc đỏ nổi bật giữa phố phường trở thành biểu tượng của khí thế và năng lượng. Với phiên bản áo đỏ mới từ GOYA, từng chi tiết được chăm chút kỹ lưỡng để mang lại sự thoải mái, dễ phối đồ nhưng vẫn toát lên tinh thần tự hào dân tộc trong từng khoảnh khắc. Mỗi bước đi trong ngày lễ Quốc khánh chính là một lời tri ân gửi đến cha ông, là niềm tự hào bất tận chảy trong tim. Khi khoác lên mình chiếc áo đỏ 2/9 từ GOYA, bạn không chỉ thể hiện tình yêu nước mà còn lan tỏa khí thế mạnh mẽ của thế hệ hôm nay. Sắc đỏ trên áo hòa quyện với niềm tự hào trong tim, để ngày 2/9 thêm rực rỡ và đáng nhớ hơn bao giờ hết. Đừng bỏ lỡ cơ hội sở hữu mẫu áo đỏ kỷ niệm 80 năm Quốc khánh 2/9 từ GOYA. Đặt hàng ngay hôm nay để cùng nhau lan tỏa niềm tự hào dân tộc trên khắp nẻo đường!"""

    cleaned = remove_stopwords(content)
    print(cleaned)
