from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/financeiro'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(254), unique=True, nullable=False)
    nome = db.Column(db.String(254), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    senha = db.Column(db.String(254), nullable=False)

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    descricao = db.Column(db.String(254), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    descricao = db.Column(db.String(254), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']


        if not cpf or not cpf.isdigit():
            flash('CPF inválido!', 'error')
            return redirect(url_for('cadastrar'))

        usuario_existente = Usuario.query.filter_by(cpf=cpf).first()
        if usuario_existente:
            flash('CPF já cadastrado!', 'error')
            return redirect(url_for('cadastrar'))

        senha_hash = generate_password_hash(senha).decode('utf-8')

        novo_usuario = Usuario(cpf=cpf, nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('entrar'))

    return render_template('cadastro.html')

@app.route('/entrar', methods=['GET'])
def login():
    return render_template('entrar.html')


@app.route('/entrar', methods=['POST'])
def entrar():
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')

    user = Usuario.query.filter_by(cpf=cpf).first()

    if user and check_password_hash(user.senha, senha):
        session['id'] = user.id
        return redirect(url_for('receita'))
    else:
        flash('CPF ou senha incorretos', 'error')
        return redirect(url_for('entrar'))


@app.route('/receita', methods=['GET'])
def adicionar():
    return render_template('receitas.html')

@app.route('/receita', methods=['POST'])
def receita():
    descricao = request.form['descricao']
    valor = request.form['valor']
    usuario_id = session['id']

    nova_receita = Receita(usuario_id=usuario_id, descricao=descricao, valor=valor)
    db.session.add(nova_receita)
    db.session.commit()

    flash('Receita cadastrada com sucesso!', 'success')
    return redirect(url_for('receita'))

@app.route('/despesa', methods=['GET'])
def adicionardespesa():
    return render_template('despesas.html')

@app.route('/despesa', methods=['POST'])
def despesa():
    descricao = request.form['descricao']
    valor = request.form['valor']
    usuario_id = session['id']

    nova_despesa = Despesa(usuario_id=usuario_id, descricao=descricao, valor=valor)
    db.session.add(nova_despesa)
    db.session.commit()

    flash('Despesa cadastrada com sucesso!', 'success')
    return redirect(url_for('despesa'))

@app.route('/')
def index():
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        return render_template('index.html', usuario=usuario)
    else:
        return render_template('index.html')


@app.route('/principal')
def principal():
    return render_template('principal.html')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(debug=True, port=8080)

