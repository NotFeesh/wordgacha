from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random, string, math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

pity = 0
coins = 100
englishOpen = open('englishopen.txt', 'r').readlines()
english10k = open('english10k.txt', 'r').readlines()
english1k = open('english1k.txt', 'r').readlines()
englishEX = open('englishEX.txt', 'r').readlines()

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(100))
  rarity = db.Column(db.String(100))
  collection = db.Column(db.String(100))
  quality = db.Column(db.Float())
  sellvalue = db.Column(db.Integer())

  def __repr__(self):
    return '<Item %r>' % self.id

class Item:
  def __init__(self, content, rarity, collection, quality, sellvalue):
    self.content = content
    self.rarity = rarity
    self.collection = collection
    self.quality = quality
    self.sellvalue = sellvalue

def roll():
  global pity
  global coins

  coins -= 10

  if pity > 99:
    roll = random.randint(91, 100)
  elif pity > 70:
    roll = random.randint(80, 100)
  else:
    roll = random.randint(1, 100)

  if roll <= 80:
    #common
    pity += 2
    quality = round(random.random(), 5)
    return Item(random.choice(string.ascii_uppercase), "Basic", "Alphabet", quality, math.floor(10 * quality))
  elif roll <= 90:
    #rare
    pity += 1
    quality = round(random.random(), 5)
    return Item(random.choice(english1k), "Commonplace", "English 1000", quality, math.floor(50 * quality))
  elif roll <= 95:
    #exquisite
    if pity >= 5:
      pity -= 5
    else:
      pity = 0
    quality = round(random.uniform(0.5, 1), 5)
    return Item(random.choice(english10k), "Exquisite", "English 10000", quality, math.floor(500 * quality))
  elif roll <= 99:
    #legendary
    if pity >= 50:
      pity -= 50
    else:
      pity = 0
    quality = round(random.uniform(0.8, 1), 5)
    return Item(random.choice(englishOpen), "Legendary", "English Open", quality, math.floor(1000 * quality))
  else:
    #supercalifragilisticexpialidocious
    pity = 0
    quality = round(random.uniform(1, 2), 5)
    return Item(random.choice(englishEX), "Supercalifragilisticexpialidocious", "English Extreme", quality, math.floor(10000 * quality))

@app.route('/', methods=['POST', 'GET'])
def index():
  global coins
  if request.method == 'POST':
    
    if (not coins < 10):
      item = roll()

      item_content = item.content
      rarity = item.rarity
      collection = item.collection
      quality = item.quality
      sellvalue = item.sellvalue
      new_item = Todo(content=item_content, rarity=rarity, collection=collection, quality=quality, sellvalue=sellvalue)

      try:
        db.session.add(new_item)
        db.session.commit()
        return redirect('/')
      except:
        return 'There was an issue adding your item :('
    else:
      return redirect('/')

  else:
    items = Todo.query.order_by(Todo.rarity.desc()).all()
    return render_template('index.html', items=items, coins=coins)

@app.route('/delete/<int:id>')
def delete(id):
  global coins

  task_to_delete = Todo.query.get_or_404(id)
  coins += task_to_delete.sellvalue
  try:
    db.session.delete(task_to_delete)
    db.session.commit()
    
    return redirect('/')
  except:
    return 'Failed to delete task :('

if __name__ == "__main__":
  app.run(debug=True)