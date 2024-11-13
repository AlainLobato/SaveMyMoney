import datetime
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import plotly.graph_objs as go
import json
import urllib.parse

NOMBRE = 2
GASTO = 3

app = Flask(__name__)

# SQLite CONNECTION
DATABASE = 'SaveMyMoney.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS TipoGasto " \
                   "(ID INTEGER PRIMARY KEY AUTOINCREMENT, Tipo TEXT NOT NULL, Descripcion TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Gastos " \
                   "(ID INTEGER PRIMARY KEY AUTOINCREMENT, TipoID INTEGER NOT NULL, Nombre TEXT NOT NULL, " \
                   "Gasto REAL NOT NULL, Fecha DATE NOT NULL DEFAULT (datetime('now', 'localtime')), " \
                   "FOREIGN KEY (TipoID) REFERENCES TipoGasto(ID))")
    conn.commit()
    conn.close()


# Settings
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TipoGasto')
    data = cursor.fetchall()
    conn.close()
    return render_template('index.html', tipo=data)

@app.route('/addTG', methods=['POST'])
def addTG():
    if request.method == 'POST':
        TIPO = request.form['Tipo']
        DESCRIPCION = request.form['Descripcion']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO TipoGasto (TIPO, DESCRIPCION) VALUES (?, ?)', (TIPO, DESCRIPCION))
        conn.commit()
        conn.close()
        flash('Tipo de gasto agregado con exito')
        return redirect(url_for('index'))

@app.route('/nuevo-tipo')
def newT():
    return render_template('addTG.html')

@app.route('/eliminar/<string:id>')
def eliminarT(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Gastos WHERE TipoID = ?', (id,))
    conn.commit()
    cursor.execute('DELETE FROM TipoGasto WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Tipo de gasto eliminado con exito')
    return redirect(url_for('index'))

@app.route('/editar/tipo-de-gasto-<string:id>')
def editT(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TipoGasto WHERE id = ?', (id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('editTG.html', t=data[0])

@app.route('/actualizar/tipo-de-gasto-<id>', methods=['POST'])
def updateT(id):
    if request.method == 'POST':
        TIPO = request.form['Tipo']
        DESCRIPCION = request.form['Descripcion']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE TipoGasto
            SET Tipo = ?,
            Descripcion = ?
            WHERE ID = ?
        """, (TIPO, DESCRIPCION, id))
        conn.commit()
        conn.close()
        flash('Tipo de gasto actualizado con exito')
        return redirect(url_for('index'))

@app.route('/gastos/<string:id>')
def gastos(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE TipoID = ?', (id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('Gastos.html', gastos=data, tipoG=id)

@app.route('/gastos/<id>/nuevo-gasto/')
def gasto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TipoGasto WHERE ID = ?', (id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('addG.html', t=data[0])

@app.route('/add/<string:tipo>', methods=['POST'])
def addG(tipo):
    if request.method == 'POST':
        NOMBRE = request.form['Nombre']
        GASTO = request.form['Gasto']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT ID FROM TipoGasto WHERE Tipo = ?', (tipo,))
        TIPOID = cursor.fetchall()
        cursor.execute('INSERT INTO Gastos (TipoID, Nombre, Gasto) VALUES (?, ?, ?)', (TIPOID[0]['ID'], NOMBRE, GASTO))
        conn.commit()
        conn.close()
        flash('Gasto agregado con exito')
        return redirect(url_for('gastos', id=TIPOID[0]['ID']))

@app.route('/gastos/editar/<string:id>')
def editG(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE id = ?', (id,))
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoGasto WHERE ID = ?', (data[0]['TipoID'],))
    tipo = cursor.fetchall()
    conn.close()
    return render_template('editG.html', g=data[0], t=tipo[0])

@app.route('/actualizar/<id>', methods=['POST'])
def updateG(id):
    if request.method == 'POST':
        NOMBRE = request.form['Nombre']
        GASTO = request.form['Gasto']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Gastos WHERE ID = ?', (id,))
        TIPOID = cursor.fetchall()
        cursor.execute("""
            UPDATE Gastos
            SET Nombre = ?,
            Gasto = ?
            WHERE ID = ?
        """, (NOMBRE, GASTO, id))
        conn.commit()
        conn.close()
        flash('Gasto actualizado con exito')
        return redirect(url_for('gastos', id=TIPOID[0]['TipoID']))

@app.route('/gastos/eliminar/<string:id>')
def eliminarG(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE ID = ?', (id,))
    ID = cursor.fetchall()
    cursor.execute('DELETE FROM Gastos WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Gasto eliminado con exito')
    return redirect(url_for('gastos', id=ID[0]['TipoID']))

@app.route('/graficos/')
def graficos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TipoGasto')
    tipos = cursor.fetchall()
    conn.close()
    return render_template('Graficos.html', tipo=tipos)

def serialize_data(data):
    rows = [[e for e in element] for element in data]
    for i, row in enumerate(rows):
        for j, element in enumerate(row):
            if type(element) == Decimal:
                rows[i][j] = float(element)
            elif type(element) == datetime.date:
                element: datetime.date = element
                rows[i][j] = element.strftime("%d-%m-%Y, %H:%M:%S")
    return rows

@app.route('/generate', methods=['POST'])
def generate():
    TIPO = request.form['Tipo']
    DISTRO = request.form['Distro']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TipoGasto WHERE TIPO = ?', (TIPO,))
    ID = cursor.fetchall()

    if DISTRO == 'Individual':
        cursor.execute('SELECT * FROM Gastos WHERE TipoID = ?', (ID[0]['ID'],))
        data = cursor.fetchall()

    elif DISTRO == 'Mensual':
        MES = request.form['Mes']
        cursor.execute('SELECT * FROM Gastos WHERE TipoID = ? AND strftime("%Y", Fecha) = strftime("%Y", "now") AND strftime("%m", Fecha) = ?', (ID[0]['ID'], MES))
        data = cursor.fetchall()

    elif DISTRO == 'Anual':
        AÑO = request.form['Anio']
        cursor.execute('SELECT * FROM Gastos WHERE TipoID = ? AND strftime("%Y", Fecha) = ?', (ID[0]['ID'], AÑO))
        data = cursor.fetchall()
    
    data_ = serialize_data(data)
    json_data = json.dumps(data_)

    conn.close()
    return redirect(url_for('graphic', info=json_data))

@app.route('/graphic/<info>')
def graphic(info):
    decoded_json_data = urllib.parse.unquote(info)
    info_data = json.loads(decoded_json_data)
    
    info_x = [i[NOMBRE] for i in info_data]
    info_y = [i[GASTO] for i in info_data]

    graph1, graph2 = create_plot(info_x, info_y)

    return render_template('newGraph.html', graphic_1=graph1, graphic_2=graph2)

def create_plot(x_data, y_data):
    fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
    fig2 = go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
    graph_1 = fig.to_html(full_html=False)
    graph_2 = fig2.to_html(full_html=False)
    
    return graph_1, graph_2

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)