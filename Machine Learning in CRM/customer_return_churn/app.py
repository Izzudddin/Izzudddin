from flask import Flask, render_template, request, redirect, session
import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pyodbc
import pickle

model = pickle.load(open('model', 'rb'))

server = '192.168.1.223'
database = 'Kurnia3'
username = 'dtAdmin'
password = 'Kcg123*#'
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

app = Flask(__name__)
app.secret_key = 'datascience'

user = {"username": "kcg", "password": "123"}

df = pd.read_sql('''
SELECT sales.no_client, sales.dt_inv, DATEDIFF(year, birthdate, '2022-01-19') 'age', no_group, sales.no_color, sales.no_size, sales.price, sales.discount, product_name, branchname, employee.name
from sales
inner join branch
on sales.no_branch = branch.no_branch
inner join customer
on sales.no_client=customer.no_client
inner join model
on sales.no_model = model.no_model
inner join model_detail
on sales.no_model = model_detail.article
inner join employee
on sales.nik = employee.nik
where branch.company = 'PD' and sales.no_client NOT LIKE '682%' and sales.no_client in (
select no_client
from sales
group by no_client
having count(distinct(dt_inv)) > 1
)
group by sales.no_client, DATEDIFF(year, birthdate, '2022-01-19'), no_group, sales.no_color,
sales.no_size, sales.price, sales.discount, product_name, branchname, employee.name, sales.dt_inv
order by dt_inv desc
                 ''', cnxn)

df2 = pd.read_sql('''
SELECT sales.no_client, sales.dt_inv, DATEDIFF(year, birthdate, '2022-01-19') 'age', no_group, sales.no_color, sales.no_size, sales.price, sales.discount, product_name, branchname, employee.name
from sales
inner join branch
on sales.no_branch = branch.no_branch
inner join customer
on sales.no_client=customer.no_client
inner join model
on sales.no_model = model.no_model
inner join model_detail
on sales.no_model = model_detail.article
inner join employee
on sales.nik = employee.nik
where branch.company = 'PD' and sales.no_client NOT LIKE '682%' and sales.no_client in (
select no_client
from sales
group by no_client
having count(distinct(dt_inv)) = 1
)
group by sales.no_client, DATEDIFF(year, birthdate, '2022-01-19'), no_group, sales.no_color,
sales.no_size, sales.price, sales.discount, product_name, branchname, employee.name, sales.dt_inv
order by dt_inv desc
                 ''', cnxn)

branch = pd.read_sql('''
select branchname
from branch
where company='PD'
''', cnxn)

churn_cust = pd.read_json('cust_churn.json')
return_cust = pd.read_json('cust_return.json')

@app.route('/')
def login():
    return render_template("base.html")

@app.route('/login', methods=['POST', 'GET'])
def auth():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        if username == user['username'] and password == user['password']:
            session['user'] = username
            return redirect('/dashboard')

        return "<h1>Wrong username or password</h1>"  # if the username or password does not matches
    return render_template("base.html")


@app.route('/dashboard')
def dashboard():
    if('user' in session and session['user'] == user['username']):
        return render_template('index.html')
    #here we are checking whether the user is logged in or not

    return '<h1>You are not logged in.</h1>'  #if the user is not in the session

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')


dash1 = dash.Dash(
        __name__,
        server=app,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        routes_pathname_prefix='/Tabel/')

dash1.layout = dbc.Container(
    [
        html.H1("Tabel Customer Churn dan Return"),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label="Return", tab_id="return"),
                dbc.Tab(label="Churn", tab_id="churn"),
            ],
            id="tabs",
            active_tab="return",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)

@dash1.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab == "return":
        return html.Div([
                dash_table.DataTable(
                            id='return',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict("rows"))])
    elif active_tab == "churn":
        return html.Div([
                dash_table.DataTable(
                            id='churn',
                            columns=[{"name": i, "id": i} for i in df2.columns],
                            data=df2.to_dict("rows"))])
    return "No tab selected"


dash2 = dash.Dash(
            __name__,
            server=app,
            routes_pathname_prefix='/graph/',
            external_stylesheets=[dbc.themes.BOOTSTRAP])

dash2.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Return and Churn Customer Prediction"),
        html.Hr(),
        dcc.Dropdown(
            id="toko",
            options=[
                {"label": col, "value": col} for col in branch['branchname']
            ],
            value=[col for col in branch['branchname']],
            multi=True,
            className="mb-3"
        ),
        dbc.Tabs(
            [dbc.Tab(label="Return", tab_id="return"),
                dbc.Tab(label="Churn", tab_id="churn"),
            ],
            id="tabs",
            active_tab="return",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)

@dash2.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")]
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and data is not None:
        if active_tab == "return":
            return dcc.Graph(figure=data["return"])
        elif active_tab == "churn":
            return dcc.Graph(figure=data["churn"])
    return "No tab selected"


@dash2.callback(
    Output('store', 'data'),
    [Input('toko', 'value')]
)
def generate_graphs(cabang):
    """
    This callback generates three simple graphs from random data.
    """
    if not cabang:
        # generate empty graphs when app loads
        return {k: go.Figure(data=[]) for k in ["return", "churn"]}
    mask = return_cust.branchname.isin(cabang)
    fig1 = px.line(return_cust[mask],
        x="tahun", y="jumlah_return", color='branchname')
    mask2 = churn_cust.branchname.isin(cabang)
    fig2 = px.line(churn_cust[mask2],
        x="tahun", y="jumlah_churn", color='branchname')

    # save figures in a dictionary for sending to the dcc.Store
    return {"return": fig1, "churn": fig2}


dash3 = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/predict/',
    external_stylesheets=[dbc.themes.BOOTSTRAP])

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Bulan Transaksi:'),
                dcc.Input(id='input1', placeholder='Bulan', type='number',
                          min=1, max=12, step=1),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Tahun Pembelian:"),
                dcc.Input(id='input2', placeholder='Tahun', type='number'),
            ]
        ),
    ],
    body=True,
)

dash3.layout = html.Div(children=[
    html.H1(children='Churn or Return Prediction', style={'textAlign': 'center'}),

    html.Div(children=[
        html.Label('Masukkan data diri customer : '),
        dcc.Input(id='input1', placeholder='Bulan', type='number', min=1, max=12, step=1),
        dcc.Input(id='input2', placeholder='Tahun', type='number'),
        dcc.Input(id='input3', placeholder='Umur', type='number', min=17, max=79, step=1),
        dcc.Dropdown(
            id='input4',
            placeholder='No Group',
            options=[
                {'label': 'OTHERSCK', 'value': '0'},
                {'label': 'PDRBELTS', 'value': '1'},
                {'label': 'PDRSCARF', 'value': '2'},
                {'label': 'PDRSCARF', 'value': '3'},
                {'label': 'PDRSOCK', 'value': '4'},
                {'label': 'PDRWLTS', 'value': '5'},
                {'label': 'PKBAGS', 'value': '6'},
                {'label': 'PKSHOES', 'value': '7'},
                {'label': 'PMBAGS', 'value': '8'},
                {'label': 'PMBRACELETS', 'value': '9'},
                {'label': 'PMSHOES', 'value': '10'},
                {'label': 'PWBAGS', 'value': '11'},
                {'label': 'PWSHOES', 'value': '12'},
                {'label': 'PWWLTS', 'value': '13'}
            ],
            value='No Group'
        ),
        dcc.Dropdown(
            id='input5',
            placeholder='Spending',
            options=[
                {'label': '0-499.000', 'value': '0'},
                {'label': '500.000-999.000', 'value': '1'},
                {'label': '1.000.000-1.499.000', 'value': '2'},
                {'label': '1.500.000-1.999.000', 'value': '3'},
                {'label': '> 2.000.000', 'value': '4'}
            ],
            value='Spending'
        ),
        dcc.Input(id='input6', placeholder='Diskon', type='number'),
        dcc.Dropdown(
            id='input7',
            placeholder='Nama Cabang',
            options=[
                {'label': 'Pedro 23 Paskal Bandung', 'value': '0'},
                {'label': 'Pedro AEON Mall BSD City', 'value': '1'},
                {'label': 'Pedro Baywalk Pluit Mall', 'value': '2'},
                {'label': 'Pedro Beachwalk Bali', 'value': '3'},
                {'label': 'Pedro Botani Square', 'value': '4'},
                {'label': 'Pedro Central Park', 'value': '5'},
                {'label': 'Pedro Centre Point Medan', 'value': '6'},
                {'label': 'Pedro Ciputra World', 'value': '7'},
                {'label': 'Pedro Deli Park Medan', 'value': '8'},
                {'label': 'Pedro Duta Mall 2 Banjarmasin', 'value': '9'},
                {'label': 'Pedro Grand City Surabaya', 'value': '10'},
                {'label': 'Pedro Grand Indonesia', 'value': '11'},
                {'label': 'Pedro Hartono Mall Yogya', 'value': '12'},
                {'label': 'Pedro Kota Kasablanka', 'value': '13'},
                {'label': 'Pedro Mall Alam Sutera', 'value': '14'},
                {'label': 'Pedro Mall Kelapa Gading 3', 'value': '15'},
                {'label': 'Pedro Mall Pondok Indah', 'value': '16'},
                {'label': 'Pedro Mall Taman Anggrek', 'value': '17'},
                {'label': 'Pedro Manado Town Square', 'value': '18'},
                {'label': 'Pedro Margo City', 'value': '19'},
                {'label': 'Pedro Online', 'value': '20'},
                {'label': 'Pedro PIK Avenue', 'value': '21'},
                {'label': 'Pedro Pacific Place', 'value': '22'},
                {'label': 'Pedro Pakuwon Mall Surabaya', 'value': '23'},
                {'label': 'Pedro Palembang Icon', 'value': '24'},
                {'label': 'Pedro Paris Van Java', 'value': '25'},
                {'label': 'Pedro Pentacity Balikpapan', 'value': '26'},
                {'label': 'Pedro Plaza Ambarukmo', 'value': '27'},
                {'label': 'Pedro Plaza Indonesia', 'value': '28'},
                {'label': 'Pedro SKA Mall Pekanbaru', 'value': '29'},
                {'label': 'Pedro Senayan City', 'value': '30'},
                {'label': 'Pedro Summarecon Mal Bekasi', 'value': '31'},
                {'label': 'Pedro Summarecon Mal Serpong', 'value': '32'},
                {'label': 'Pedro Sun Plaza Medan', 'value': '33'},
                {'label': 'Pedro Tunjungan Plaza Surabaya', 'value': '34'}
            ],
            value='Nama Cabang'
        ),
        html.Div(id='result')
    ], style={'textAlign': 'center'}),
])

@dash3.callback(
    Output(component_id='result', component_property='children'),
    [Input(component_id='input1', component_property='value'),
    Input(component_id='input2', component_property='value'),
    Input(component_id='input3', component_property='value'),
    Input(component_id='input4', component_property='value'),
    Input(component_id='input5', component_property='value'),
    Input(component_id='input6', component_property='value'),
     Input(component_id='input7', component_property='value')])
def update_years_of_experience_input(input1, input2, input3, input4, input5, input6, input7):
    try:
        prediction = model.predict([[int(input1),int(input2),int(input3),int(input4), int(input5),int(input6),int(input7)]])
        return 'Prediction is {}'.format(prediction)
    except ValueError:
        return 'Unable to give prediction'