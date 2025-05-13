import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from teacher.models import Course


class ChineseTextProcessor:
    """中文文本处理器"""
    def __init__(self):
        self.stopwords = self.load_stopwords()
        jieba.initialize()  # 初始化jieba分词

    def load_stopwords(self):
        """加载中文停用词表"""
        with open('static/text/stopwords.txt', 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f])

    def preprocess(self, text):
        """中文文本预处理"""
        # 1. 清洗特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        # 2. 分词
        words = jieba.lcut(text)
        # 3. 去除停用词和单字
        return ' '.join([
            word for word in words
            if word not in self.stopwords
        ])

class CourseRecommender:
    def __init__(self):
        self.processor = ChineseTextProcessor()  # 初始化处理器

    def get_recommendations(self,student, top_n=5):
        """获取课程推荐列表
        Args:
            student: 学生对象实例
            top_n: 返回推荐数量

        Returns:
            按相似度排序的课程QuerySet
        """
        # 获取学生已选课程
        enrolled_courses = student.courses.all()
        if not enrolled_courses.exists():
            return Course.objects.order_by('-numbers')[:top_n]  # 无选课时返回热门课程

        # 获取候选课程（排除已选课程）
        enrolled_ids = enrolled_courses.values_list('course_id', flat=True)
        candidate_courses = Course.objects.exclude(course_id__in=enrolled_ids)


        # 中文预处理
        enrolled_descriptions = [self.processor.preprocess(c.description) for c in enrolled_courses]
        candidate_descriptions = [self.processor.preprocess(c.description) for c in candidate_courses]
        all_texts = enrolled_descriptions + candidate_descriptions

        # TF-IDF向量化
        vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            max_features=5000  # 控制特征维度
        )
        # vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # 分割矩阵：已选课程向量 vs 候选课程向量
        enrolled_vectors = tfidf_matrix[:len(enrolled_descriptions)]
        candidate_vectors = tfidf_matrix[len(enrolled_descriptions):]

        # 计算余弦相似度
        similarity_matrix = cosine_similarity(enrolled_vectors, candidate_vectors)

        # 聚合相似度（取每列最大值）
        max_similarities = similarity_matrix.max(axis=0)

        # 生成排序索引
        sorted_indices = max_similarities.argsort()[::-1]

        # 获取推荐课程ID
        recommended_ids = [
            candidate_courses[int(i)].course_id
            for i in sorted_indices[:top_n]
        ]

        # 保持原始数据库排序
        return Course.objects.filter(course_id__in=recommended_ids).order_by('-numbers')
