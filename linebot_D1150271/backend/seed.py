import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.models import Poem

# Create tables
Base.metadata.create_all(bind=engine)

def seed_poems():
    db = SessionLocal()
    if db.query(Poem).count() == 0:
        poems = [
            Poem(title="第一籤", fortune_type="大吉", content="巍巍獨步向雲間，玉殿千官第一班。富貴榮華天更與，結成金誥蘊秋山。", explanation="凡事大吉，所求必應。"),
            Poem(title="第二籤", fortune_type="中平", content="鯨魚未變守江河，不可干戈弄網羅。異日樽迎身變化，許君一躍過天河。", explanation="目前時機未到，需等待時機。"),
            Poem(title="第三籤", fortune_type="下下", content="燕子秋期悲客旅，隨波逐流任風霜。孤帆遠影碧空盡，唯見長江天際流。", explanation="諸事不順，宜守舊，不宜躁進。")
        ]
        db.add_all(poems)
        db.commit()
        print("Poem database seeded successfully!")
    else:
        print("Poems already exist.")
    db.close()

if __name__ == "__main__":
    seed_poems()
