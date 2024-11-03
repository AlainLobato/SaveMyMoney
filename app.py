from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)

#SQLSERVER CONNECTION
app.config['SQL_SERVER_DRIVER'] = 'ODBC Driver 17 for SQL Server'
app.config['SQL_SERVER_SERVER'] = 'localhost'
app.config['SQL_SERVER_DATABASE'] = 'SaveMyMoney'

connection_string = (
    f"DRIVER={app.config['SQL_SERVER_DRIVER']};"
    f"SERVER={app.config['SQL_SERVER_SERVER']};"
    f"DATABASE={app.config['SQL_SERVER_DATABASE']};"
    "Trusted_Connection=yes;"
)

mysql = pyodbc.connect(connection_string)


#Settings
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM TipoGasto')
    data = cursor.fetchall()
    return render_template('index.html', tipo = data)

@app.route('/addTG', methods=['POST'])
def addTG():
    if(request.method == 'POST'):
        TIPO = request.form['Tipo']
        DESCRIPCION = request.form['Descripcion']
        cursor = mysql.cursor()
        cursor.execute('INSERT INTO TipoGasto (TIPO, DESCRIPCION) VALUES (?, ?)', (TIPO, DESCRIPCION))
        mysql.commit()
        flash('Tipo de gasto agregado con exito')
        return redirect(url_for('index'))

@app.route('/nuevo-tipo')
def newT():
    return render_template('addTG.html')

@app.route('/eliminar/<string:id>')
def eliminarT(id):
    cursor = mysql.cursor()
    cursor.execute('DELETE FROM Gastos WHERE TipoID = ?', id)
    mysql.commit()
    cursor.execute('DELETE FROM TipoGasto WHERE ID = ?', id)
    mysql.commit()
    flash('Tipo de gasto eliminado con exito')
    return redirect(url_for('index'))

@app.route('/editar/tipo-de-gasto-<string:id>')
def editT(id):
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM TipoGasto WHERE id = ?', id)
    data = cursor.fetchall()
    return render_template('editTG.html', t = data[0])

@app.route('/actualizar/tipo-de-gasto-<id>', methods=['POST'])
def updateT(id):
    if request.method == 'POST':
        TIPO = request.form['Tipo']
        DESCRIPCION = request.form['Descripcion']

        cursor = mysql.cursor()
        cursor.execute("""
            UPDATE TipoGasto
            SET Tipo = ?,
            Descripcion = ?
            WHERE ID = ?
        """, (TIPO, DESCRIPCION, id))
        mysql.commit()
        flash('Tipo de gasto actualizado con exito')
        return redirect(url_for('index'))

@app.route('/gastos/<string:id>')
def gastos(id):
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE TipoID = ?', id)
    data = cursor.fetchall()
    return render_template('Gastos.html', gastos = data, tipoG = id)

@app.route('/gastos/<id>/nuevo-gasto/')
def gasto(id):
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM TipoGasto WHERE ID = ?', id)
    data = cursor.fetchall()
    return render_template('addG.html', t = data[0])
    
@app.route('/add/<string:tipo>', methods=['POST'])
def addG(tipo):
    if(request.method == 'POST'):
        NOMBRE = request.form['Nombre']
        GASTO = request.form['Gasto']
        cursor = mysql.cursor()
        cursor.execute('SELECT ID FROM TipoGasto WHERE Tipo = ?', tipo)
        TIPOID = cursor.fetchall()
        cursor.execute('INSERT INTO Gastos (TipoID, Nombre, Gasto) VALUES (?, ?, ?)', (TIPOID[0].ID, NOMBRE, GASTO))
        mysql.commit()
        flash('Gasto agregado con exito')
        return redirect(url_for('gastos', id=TIPOID[0].ID))
    
@app.route('/gastos/editar/<string:id>')
def editG(id):
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE id = ?', id)
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoGasto WHERE ID = ?', data[0].TipoID)
    tipo = cursor.fetchall()
    return render_template('editG.html', g = data[0], t = tipo[0])

@app.route('/actualizar/<id>', methods=['POST'])
def updateG(id):
    if request.method == 'POST':
        NOMBRE = request.form['Nombre']
        GASTO = request.form['Gasto']
        cursor = mysql.cursor()

        cursor.execute('SELECT * FROM Gastos WHERE ID = ?', id)
        TIPOID = cursor.fetchall()

        cursor.execute("""
            UPDATE Gastos
            SET Nombre = ?,
            Gasto = ?
            WHERE ID = ?
        """, (NOMBRE, GASTO, id))

        mysql.commit()
        flash('Gasto actualizado con exito')
        return redirect(url_for('gastos', id=TIPOID[0].TipoID))

@app.route('/gastos/eliminar/<string:id>')
def eliminarG(id):
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM Gastos WHERE ID = ?', id)
    ID = cursor.fetchall()
    cursor.execute('DELETE FROM Gastos WHERE ID = ?', id)
    mysql.commit()
    flash('Gasto eliminado con exito')
    return redirect(url_for('gastos', id=ID[0].TipoID))

if(__name__ == '__main__'):
    app.run(port=3000, debug = True)