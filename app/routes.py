from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from app import db
from app.models import (
    CANAIS_VENDA,
    REGIOES,
    STATUS_PERMITIDOS,
    TIPOS_OCORRENCIA,
    Acompanhamento,
    Ocorrencia,
    Pedido,
    Regiao,
)

bp = Blueprint("main", __name__)


def _pedido_or_404(identificador):
    return db.one_or_404(select(Pedido).where(Pedido.identificador == identificador))


@bp.get("/")
def index():
    identificador = request.args.get("identificador", "").strip()
    regiao = request.args.get("regiao", "").strip()
    canal = request.args.get("canal", "").strip()
    query = select(Pedido).join(Pedido.regiao).order_by(Pedido.id)
    if identificador:
        query = query.where(Pedido.identificador.ilike(f"%{identificador}%"))
    if regiao:
        query = query.where(Regiao.nome == regiao)
    if canal:
        query = query.where(Pedido.canal_venda == canal)
    pedidos = db.session.execute(query).scalars().all()
    return render_template(
        "index.html",
        pedidos=pedidos,
        regioes=REGIOES,
        canais=CANAIS_VENDA,
        filtros={"identificador": identificador, "regiao": regiao, "canal": canal},
    )


@bp.route("/pedidos/novo", methods=("GET", "POST"))
def novo_pedido():
    if request.method == "POST":
        dados = request.form
        obrigatorios = ["destinatario", "destino", "regiao", "canal_venda", "descricao_volume", "status"]
        if any(not dados.get(campo, "").strip() for campo in obrigatorios):
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("pedido_form.html", form=dados, **_form_options())
        if dados["status"] not in STATUS_PERMITIDOS:
            flash("O status informado não é permitido.", "erro")
            return render_template("pedido_form.html", form=dados, **_form_options())
        regiao = db.session.scalar(select(Regiao).where(Regiao.nome == dados["regiao"]))
        identificador = _proximo_identificador()
        pedido = Pedido(
            identificador=identificador,
            destinatario=dados["destinatario"].strip(),
            destino=dados["destino"].strip(),
            regiao=regiao,
            canal_venda=dados["canal_venda"],
            descricao_volume=dados["descricao_volume"].strip(),
            status=dados["status"],
        )
        db.session.add(pedido)
        db.session.flush()
        db.session.add(
            Acompanhamento(
                pedido=pedido,
                status=pedido.status,
                observacao="Pedido cadastrado no sistema.",
            )
        )
        _add_ocorrencia_if_present(pedido, dados)
        db.session.commit()
        flash(f"Pedido {identificador} cadastrado com sucesso.", "sucesso")
        return redirect(url_for("main.detalhe_pedido", identificador=identificador))
    return render_template("pedido_form.html", form={}, **_form_options())


@bp.get("/pedidos/<identificador>")
def detalhe_pedido(identificador):
    pedido = _pedido_or_404(identificador)
    return render_template(
        "pedido_detalhe.html",
        pedido=pedido,
        status_permitidos=STATUS_PERMITIDOS,
        tipos_ocorrencia=TIPOS_OCORRENCIA,
    )


@bp.post("/pedidos/<identificador>/status")
def atualizar_status(identificador):
    pedido = _pedido_or_404(identificador)
    novo_status = request.form.get("status", "")
    observacao = request.form.get("observacao", "").strip()
    if novo_status not in STATUS_PERMITIDOS:
        flash("Selecione um status válido.", "erro")
    else:
        pedido.status = novo_status
        db.session.add(
            Acompanhamento(
                pedido=pedido,
                status=novo_status,
                observacao=observacao or f"Status atualizado para {novo_status}.",
            )
        )
        db.session.commit()
        flash("Status atualizado e histórico preservado.", "sucesso")
    return redirect(url_for("main.detalhe_pedido", identificador=identificador))


@bp.post("/pedidos/<identificador>/ocorrencias")
def registrar_ocorrencia(identificador):
    pedido = _pedido_or_404(identificador)
    tipo = request.form.get("tipo", "")
    descricao = request.form.get("descricao", "").strip()
    providencia = request.form.get("providencia", "").strip()
    if tipo not in TIPOS_OCORRENCIA or not descricao:
        flash("Informe um tipo válido e descreva a ocorrência.", "erro")
    else:
        db.session.add(
            Ocorrencia(
                pedido=pedido,
                tipo=tipo,
                descricao=descricao,
                providencia=providencia or None,
            )
        )
        db.session.commit()
        flash("Ocorrência registrada com sucesso.", "sucesso")
    return redirect(url_for("main.detalhe_pedido", identificador=identificador))


def _form_options():
    return {
        "regioes": REGIOES,
        "canais": CANAIS_VENDA,
        "status_permitidos": STATUS_PERMITIDOS,
        "tipos_ocorrencia": TIPOS_OCORRENCIA,
    }


def _proximo_identificador():
    maior = db.session.scalar(select(Pedido.identificador).order_by(Pedido.id.desc()).limit(1))
    return str(int(maior) + 1) if maior and maior.isdigit() else "1001"


def _add_ocorrencia_if_present(pedido, dados):
    tipo = dados.get("tipo_ocorrencia", "")
    descricao = dados.get("descricao_ocorrencia", "").strip()
    providencia = dados.get("providencia", "").strip()
    if tipo and descricao and tipo in TIPOS_OCORRENCIA:
        db.session.add(
            Ocorrencia(
                pedido=pedido,
                tipo=tipo,
                descricao=descricao,
                providencia=providencia or None,
            )
        )
