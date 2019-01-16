from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_mysqldb import MySQL
import time



#Mysql Connection
app = Flask(__name__)
app.config['MYSQL_HOST']= 'localhost' 
app.config['MYSQL_USER']= 'root' 
app.config['MYSQL_PASSWORD']= 'localhost' 
app.config['MYSQL_DB']= 'Venta' 
mysql = MySQL(app)


#Session
app.secret_key = 'mysecretkey'



@app.route('/')
def index():
	return render_template('Login.html')


#***************************************************************


@app.route('/usuario')
def usuario():
	cur =  mysql.connection.cursor()
	cur.execute('SELECT * FROM usuario where status_usu= 1')
	datos = cur.fetchall()
	return render_template('admin/registrarU.html', contact = datos )

@app.route('/baja/<string:id>')	
def bajaUsu(id):
	str(id)
	cur = mysql.connection.cursor()
	cur.execute('UPDATE  usuario set status_usu =  0 where usuario_usu = "{0}" '.format(id))
	mysql.connection.commit()
	flash('Contacto dado de baja con exito')
	return redirect(url_for('usuario'))


@app.route('/regUsu', methods=['POST'])
def regUsu():
	if request.method == 'POST':
		user = request.form['user']
		password = request.form['password']
		rol = request.form['rol']
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO usuario VALUES(%s,%s, %s, 1)',(user, password,rol))
		mysql.connection.commit()
		flash('Usuario agregado con exito')
		return render_template('Vista_Admin.html')


#Producto ***********************************************************
@app.route('/producto')
def producto():
	registrar = ('registrar')
	if registrar:
		return render_template('producto/registrarP.html')
	elif mod:
	    return render_template('Vista_Admin.html')

@app.route('/regPro', methods=['POST'])
def regPro():
	if request.method == 'POST':
		codigo = request.form['codigo']
		nombre = request.form['nombre']
		unidad = request.form['unidad']
		categoria = request.form['categoria']
		minimo = request.form['minimo']
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO producto VALUES(%s,%s, %s, 0, %s, %s)',(codigo, nombre, unidad, categoria, minimo))
		mysql.connection.commit()
		flash('Producto agregado con exito')
		return render_template('Vista_Admin.html')

#/*********************************************************************

#Resurtir**************************************************************
@app.route('/lista_cod')
def lista_cod():
	cur =  mysql.connection.cursor()
	cur.execute('SELECT codigo_pro FROM producto')
	datos = cur.fetchall()
	return render_template('producto/resurtir.html', contact = datos )

@app.route('/pag_res')
def pag_res():
	return redirect(url_for('lista_cod'))


@app.route('/resurtir', methods=['POST'])
def resurtir():
	if request.method == 'POST':
		codigo = request.form['codigo']
		fecha = time.strftime("%Y-%m-%d")
		cantidad = request.form['cantidad']
		costoR = request.form['costoR']
		costoU = request.form['costoU']
		precio = request.form['precio']
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO resurtir VALUES(null, "'+codigo+'", "'+fecha+'", '+cantidad+', '+costoR+', '+costoU+' )')
		mysql.connection.commit()
		cur.execute('UPDATE producto SET precio_pro = "'+precio+'" where codigo_pro= "'+codigo+'" ')
		mysql.connection.commit()
		flash('Producto resurtido con exito')
		return render_template('Vista_Admin.html')	


#/*********************************************************************


#Corte_Caja***********************************************************
@app.route('/regresar')
def regresar():
	return render_template('Vista_Admin.html')

@app.route('/regresar2')
def regresar2():
	return render_template('Inicio.html')
	

@app.route('/corte')
def corte():
	cur = mysql.connection.cursor()
	fecha = time.strftime("%Y-%m-%d")
	cur.execute('select sum(total_ven) from venta where fecha_ven="'+fecha+'" ')
	subtotal = cur.fetchone()
	total = str(subtotal[0])
	flash(total)
	return render_template("admin/corteCaja.html")

@app.route('/cortexCaja')
def cortexCaja():
	id= session['usu']
	cur = mysql.connection.cursor()
	fecha = time.strftime("%Y-%m-%d")
	cur.execute('select sum(total_ven) from venta where fecha_ven="'+fecha+'" and usuario_usu= "'+id+'" ')
	subtotal = cur.fetchone()
	total = str(subtotal[0])
	flash(total)
	return render_template("Corte_x_Caja.html")


#/********************************************************************
@app.route('/pago')
def pago():
	id= session['uno']
	cur = mysql.connection.cursor()
	cur.execute('select sum(subtotal_pro) from renglon_venta where  id_ven="'+id+'"')
	subtotal = cur.fetchone()
	total = str(subtotal[0])
	print(total)
	cur.execute('update venta set total_ven = "'+total+'", status_ven=1 where id_ven= "'+id+'" ')
	mysql.connection.commit()
	flash(total)
	return render_template("Pago.html")


@app.route('/venta')
def venta():
	usu = session['usu']
	cur = mysql.connection.cursor()
	fecha = time.strftime("%Y-%m-%d")
	cur.execute('insert into venta values(null, "'+fecha+'" , "'+usu+'",0, 0)')
	mysql.connection.commit()
	cur.execute('select last_insert_id()')
	cve = cur.fetchone()
	session['uno'] = str(cve[0])
	flash(fecha)
	return render_template('Inicio.html')


@app.route('/verificar', methods=['POST'])	
def verificar():
	if request.method == 'POST':
		user = request.form['user']
		password = request.form['password']
		fecha = time.strftime("%Y-%m-%d")
		cur = mysql.connection.cursor()
		cur.execute('SELECT rol_usu FROM  usuario WHERE usuario_usu = %s and password_usu = %s and status_usu= 1',(user, password))
		datos = cur.fetchone()
		if datos:
			print(str(datos[0]))
			session['usu'] = user
			if datos[0] == "Caja":
				return redirect(url_for('venta'))
			elif datos[0] == "Admin":
				return render_template('Vista_Admin.html')
			flash('No existe ese usuario')
			return redirect(url_for('index'))

		else:
			flash('No existe ese usuario')
			return redirect(url_for('index'))


@app.route('/articulo', methods=['POST'])
def articulo():
	if request.method == 'POST':
		id= session['uno']
		codigo = request.form['codigo']
		cantidad = request.form['cantidad']
		cur = mysql.connection.cursor()
		cur.execute('select precio_pro from producto where codigo_pro ="'+codigo+'"')
		precio = cur.fetchone()
		print(precio[0]*cantidad)
		subtotal = (str(precio[0]))
		sub = int(cantidad) * int(subtotal)
		cur.execute('insert into renglon_venta values(null, "'+codigo+'", '+str(id)+','+cantidad+', '+str(sub)+', 1)')
		mysql.connection.commit()

		cur.execute('SELECT * FROM renglon_venta  rv join producto  p on p.codigo_pro= rv.codigo_pro where id_ven = '+id+'  order by id_reg')
		var = cur.fetchall()
		return render_template('Inicio.html', contact = var)  



if __name__ ==  '__main__':
	app.run(debug = True)