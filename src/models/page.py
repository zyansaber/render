# src/models/page.py

from src.models import db

class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    page_type = db.Column(db.String(20), default='powerbi')  # 新增：区分类型
    powerbi_embed_url = db.Column(db.String(500), nullable=True)
    custom_url = db.Column(db.String(500), nullable=True)  # 新增：自定义链接
    content_html = db.Column(db.Text, nullable=True)        # 新增：富文本内容（含图片/HTML）
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Page {self.title}>'
