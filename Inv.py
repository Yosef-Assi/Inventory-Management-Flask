from flask import Flask, render_template,request, redirect ,session,flash
from flask_sqlalchemy import SQLAlchemy  
from sqlalchemy.sql import func

app = Flask(__name__)    # Create a new instance of the Flask class called "app"
app.secret_key = 'keep it secret, keep it safe' #for session
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///registration.db' #for database
db = SQLAlchemy(app)    

class Product(db.Model) :
    product_id=db.Column(db.String(200), primary_key=True , nullable = False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    product_movement = db.relationship('ProductMovement', backref='productsMov')
    def __repr__(self):
        return f'<Product {self.product_id}>'

class Location(db.Model) :
    location_id=db.Column(db.String(200), primary_key=True , nullable = False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f'<Location {self.location_id}>'                               


class ProductMovement(db.Model) :
    movement_id=db.Column(db.Integer, primary_key=True , nullable = False)
    timestamp = db.Column(db.DateTime(timezone=True),server_default=func.now())
    from_location = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable = True)
    to_location = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable = True)
    product_id = db.Column(db.String(200), db.ForeignKey('product.product_id'))
    location_from = db.relationship('Location', foreign_keys=from_location)
    location_to  = db.relationship('Location', foreign_keys=to_location)
    qty = db.Column(db.Integer)

    def __repr__(self):
        return f'<Location {self.movement_id}>'
    

##APP Pages##
@app.route('/addProduct')
def addProduct():
    return render_template("addProduct.html")

@app.route('/addLocation')
def addLocation():
    return render_template("addLocation.html")

@app.route('/addProductMovement')
def addProductMovement():
    all_location=Location.query.all()
    all_product=Product.query.all()

    return render_template("addProductMovement.html",all_location=all_location,all_product=all_product)

@app.route('/updateProduct/<product_id>')
def updateProduct(product_id):
    product = Product.query.get(product_id)
    return render_template("updateProduct.html",product=product)

@app.route('/updateLocation/<location_id>')
def updateLocation(location_id):
    location = Location.query.get(location_id)
    return render_template("updateLocation.html",location=location)

@app.route('/updateMovement/<movement_id>')
def updateMovement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    all_location=Location.query.all()
    all_product=Product.query.all()
    return render_template("updateMovement.html",movement=movement,all_location=all_location,all_product=all_product)



##APP Pages##



####Add/Show Product#######

@app.route('/product', methods=['POST'])
def create_product():
    if len(request.form['product_id']) < 1:
        flash("Please enter a product name")
    if not '_flashes' in session.keys():
        product_name = request.form["product_id"]
        new_product = Product(product_id=product_name)
        db.session.add(new_product)
        db.session.commit()
        flash("Product successfully added!")
    return redirect("/addProduct")
        
@app.route("/product")
def show_product():
    all_product=Product.query.all()
    return render_template("product.html",all_product=all_product)
####Add/Show Product#######


####Update Product#######

@app.route('/updateProduct/<product_name>', methods=["POST"])
def update_Product(product_name):
    current_product = Product.query.get(product_name)
    before_update_porduct = current_product.product_id
    new_update_product = request.form['product_id']
    current_product.product_id = request.form['product_id']
    db.session.commit()
    update_product_movements(before_update_porduct, new_update_product)
    return redirect("/product")

def update_product_movements(before_update_porduct, new_update_product):
    productInMovement = ProductMovement.query.filter(ProductMovement.product_id == before_update_porduct).all()
    for product in productInMovement:
        product.product_id = new_update_product
    db.session.commit()

####Update Product#######


####Add/Show Location#######

@app.route('/location', methods=['POST'])  
def create_location():
    if len(request.form['location_id']) < 1:
        flash("Please enter a location name")
    if not '_flashes' in session.keys(): 
        location_id = request.form["location_id"]
        new_location = Location(location_id=location_id)
        db.session.add(new_location)
        db.session.commit()
        flash("Location successfully added!")
    return redirect("/addLocation")


@app.route("/locations")
def show_location():
    all_location=Location.query.all()
    return render_template("locations.html",all_location=all_location)

####Add/Show Location#######


####Update Location#######

@app.route('/updateLocation/<location_name>', methods=["POST"])
def update_location(location_name):
    current_location = Location.query.get(location_name)
    before_update_location = current_location.location_id
    new_update_location = request.form['location_id']
    current_location.location_id = request.form['location_id']
    db.session.commit()
    update_location_movements(before_update_location, new_update_location)
    return redirect("/locations")

def update_location_movements(before_update_location, new_update_location):
    fromLocationInMovement = ProductMovement.query.filter(ProductMovement.from_location == before_update_location).all()
    for from_location in fromLocationInMovement:
        from_location.from_location = new_update_location

    toLocationInMovement = ProductMovement.query.filter(ProductMovement.to_location == before_update_location).all()
    for to_location in toLocationInMovement:
        to_location.to_location = new_update_location
    db.session.commit()

####Update Location#######


####Add/Show Movement#######

@app.route('/addProductMovement', methods=['POST'])
def create_productMovement():
    if len(request.form['fromLocation']) < 1 and len(request.form['toLocation']) < 1 :
        flash("from location and to location cant both null")
    if len(request.form['quantity']) < 1 :
        flash("Please enter the quantity")
    if not '_flashes' in session.keys():
        from_location = request.form["fromLocation"]
        to_location = request.form["toLocation"]
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]
        new_movement = ProductMovement(from_location=from_location,to_location=to_location,product_id=product_id,qty=quantity)
        db.session.add(new_movement)
        db.session.commit()
        flash("Movement successfully added!")
    return redirect("/addProductMovement")
        
@app.route("/movement")
def show_movements():
    all_movement=ProductMovement.query.all()
    return render_template("productMovement.html",all_movement=all_movement)


####Add/Show Movement#######




####Update Movement#######

@app.route('/updateMovement/<movement_id>', methods=["POST"])
def update_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    movement.from_location = request.form["fromLocation"]
    movement.to_location = request.form["toLocation"]
    movement.product_id = request.form["product_id"]
    movement.qty = request.form["quantity"]

    db.session.commit()
    return redirect("/movement")



####Update Movement#######


@app.route("/")
def product_balance():
        qry = db.session.query(
            ProductMovement.product_id,
            ProductMovement.to_location,

            func.sum(ProductMovement.qty),
            ProductMovement.from_location,

                 )
        qry = qry.group_by(ProductMovement.product_id,ProductMovement.to_location)
        productBal2=qry.all()
        return render_template("productBalance.html",productBal=productBal2)
if __name__=="__main__":       
    app.run(debug=True)    

