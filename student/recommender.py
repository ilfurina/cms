# student/recommender.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from teacher.models import Course


class CourseRecommender:
    @staticmethod
    def get_recommendations(student, top_n=5):
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

        # 准备文本数据
        enrolled_descriptions = [c.description for c in enrolled_courses]
        candidate_descriptions = [c.description for c in candidate_courses]
        all_texts = enrolled_descriptions + candidate_descriptions

        # TF-IDF向量化
        vectorizer = TfidfVectorizer(stop_words='english')
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
