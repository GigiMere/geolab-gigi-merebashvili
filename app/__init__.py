from app import app
from app import checkout,contact,edit_product,upload_image,admin_panel,logout,login,register,cart,product,home,init_db,setup,get_db_connection,allowed_file

if __name__ == "__main__":
    app.run(debug=False)


