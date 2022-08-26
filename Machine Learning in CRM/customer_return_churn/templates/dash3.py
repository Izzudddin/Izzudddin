import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pickle

app = dash.Dash()
model = pickle.load(open('model', 'rb'))

app.layout = html.Div(children=[
    html.H1(children='Spending Prediction', style={'textAlign': 'center'}),

    html.Div(children=[
        html.Label('Masukkan data diri customer : '),
        dcc.Dropdown(
            id='input1',
            options=[
                {'label': 'Employee', 'value': '0'},
                {'label': 'Entrepreneur', 'value': '1'},
                {'label': 'Housewife', 'value': '2'},
                {'label': 'Karyawan Swasta', 'value': '3'},
                {'label': 'Others', 'value': '4'},
                {'label': 'Professional', 'value': '5'},
                {'label': 'Sudent', 'value': '6'}
            ],
            value='Pekerjaan'
        ),
        dcc.Dropdown(
            id='input2',
            options=[
                {'label': 'Budha', 'value': '0'},
                {'label': 'Hindu', 'value': '1'},
                {'label': 'Islam', 'value': '2'},
                {'label': 'Katolik', 'value': '0'},
                {'label': 'Konghucu', 'value': '1'},
                {'label': 'Kristen', 'value': '2'},
                {'label': 'Others', 'value': '0'}
            ],
            value='Agama'
        ),
        dcc.Dropdown(
            id='input3',
            options=[
                {'label': 'MALE', 'value': '0'},
                {'label': 'FEMALE', 'value': '1'}
            ],
            value='Jenis Kelamin'
        ),
        dcc.Input(id='input4', type='number', min=0, max=100, step=1),
        dcc.Dropdown(
            id='input5',
            options=[
                {'label': 'BALI', 'value': '0'},
                {'label': 'BALIKPAPAN', 'value': '1'},
                {'label': 'BANDUNG', 'value': '2'},
                {'label': 'BANJARMASIN', 'value': '0'},
                {'label': 'BEKASI', 'value': '1'},
                {'label': 'BOGOR', 'value': '2'},
                {'label': 'JAKARTA', 'value': '0'},
                {'label': 'MEDAN', 'value': '1'},
                {'label': 'MANADO', 'value': '2'},
                {'label': 'PALEMBANG', 'value': '0'},
                {'label': 'PEKANBARU', 'value': '1'},
                {'label': 'SURABAYA', 'value': '2'},
                {'label': 'YOGYAKARTA', 'value': '2'}
            ],
            value='Kota'
        ),
        dcc.Dropdown(
            id='input6',
            options=[
                {'label': 'Pedro 23 Paskal Bandung', 'value': '0'},
                {'label': 'Pedro AEON Mall BSD City', 'value': '1'},
                {'label': 'Pedro Baywalk Pluit Mall', 'value': '2'},
                {'label': 'Pedro Beachwalk Bali', 'value': '0'},
                {'label': 'Pedro Botani Square', 'value': '1'},
                {'label': 'Pedro Central Park', 'value': '2'},
                {'label': 'Pedro Deli Park Medan', 'value': '0'},
                {'label': 'Pedro Duta Mall 2 Banjarmasin', 'value': '1'},
                {'label': 'Pedro Grand City Surabaya', 'value': '2'},
                {'label': 'Pedro Grand Indonesia', 'value': '0'},
                {'label': 'Pedro Hartono Mall Yogya', 'value': '1'},
                {'label': 'Pedro Kota Kasablanka', 'value': '2'},
                {'label': 'Pedro Mall Alam Sutera', 'value': '0'},
                {'label': 'Pedro Mall Kelapa Gading 3', 'value': '1'},
                {'label': 'Pedro Mall Pondok Indah', 'value': '2'},
                {'label': 'Pedro Mall Taman Anggrek', 'value': '0'},
                {'label': 'Pedro Manado Town Square', 'value': '1'},
                {'label': 'Pedro Margo City', 'value': '2'},
                {'label': 'Pedro Online', 'value': '0'},
                {'label': 'Pedro PIK Avenue', 'value': '1'},
                {'label': 'Pedro Pacific Place', 'value': '2'},
                {'label': 'Pedro Pakuwon Mall Surabaya', 'value': '0'},
                {'label': 'Pedro Palembang Icon', 'value': '1'},
                {'label': 'Pedro Paris Van Java', 'value': '2'},
                {'label': 'Pedro Pentacity Balikpapan', 'value': '2'},
                {'label': 'Pedro Plaza Ambarukmo', 'value': '0'},
                {'label': 'Pedro Plaza Indonesia', 'value': '1'},
                {'label': 'Pedro SKA Mall Pekanbaru', 'value': '2'},
                {'label': 'Pedro Senayan City', 'value': '0'},
                {'label': 'Pedro Summarecon Mal Bekasi', 'value': '1'},
                {'label': 'Pedro Summarecon Mal Serpong', 'value': '2'},
                {'label': 'Pedro Sun Plaza Medan', 'value': '0'},
                {'label': 'Pedro Tunjungan Plaza Surabaya', 'value': '1'}
            ],
            value='Nama Cabang'
        ),
        html.Div(id='result')
    ], style={'textAlign': 'center'}),
])

@app.callback(
    Output(component_id='result', component_property='children'),
    [Input(component_id='input1', component_property='value'),
    Input(component_id='input2', component_property='value'),
    Input(component_id='input3', component_property='value'),
    Input(component_id='input4', component_property='value'),
    Input(component_id='input5', component_property='value'),
    Input(component_id='input6', component_property='value')])

def update_years_of_experience_input(input1, input2, input3, input4, input5, input6):
    try:
        prediction = model.predict([[int(input1),int(input2),int(input3),int(input4), int(input5), int(input6)]])
        return 'Prediction is {}'.format(prediction)
    except ValueError:
        return 'Unable to give prediction'

if __name__ == '__main__':
    app.run_server(debug=True)