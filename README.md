# Stock_management
A real-time stock trading platform with order matching engine built with Django REST Framework. Users can register, login, browse stocks, place buy/sell orders, and track their portfolio with live balance updates.

1.First of all u have to create a virtual enviornment 
python -m venv venv
venv\Scripts\activate

2.  Install Dependencies
pip install -r requirements.txt

3. Configure Database
python manage.py makemigrations
python manage.py migrate

4. Create Superuser (It's optional if u want to access the admin panel than createsuper user)
python manage.py createsuperuser

5. Run Server
python manage.py runserver
Server will start at: http://127.0.0.1:8000/ 

our EndPoints

POST	/api/register/	User registration	
POST	/api/login/	User login	
GET	/api/stocks/	List all stocks	
GET	/api/stocks/search/?q=	Search stocks	
GET	/api/orders/	Get user orders	
POST	/api/orders/	Place new order	
GET	/api/holdings/	User portfolio

6. Authentication
After login, include the token in all request headers:
Authorization: Token your-auth-token-here


7. Database Schema
User - User accounts with balances
Stock - Available stocks for trading
Order - Buy/Sell orders
Trade - Completed trades
UserHolding - User's stock portfolio

