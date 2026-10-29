from datetime import datetime, timezone

from app import db

STATUS_PERMITIDOS = ("Pendente", "Em andamento", "Entregue", "Devolvido")
TIPOS_OCORRENCIA = ("Atraso", "Devolução", "Ausência de entregador", "Outro")
REGIOES = ("Centro", "Norte", "Sul", "Leste", "Oeste")
CANAIS_VENDA = ("Loja virtual", "Marketplace", "Loja física", "Telefone")


class Regiao(db.Model):
    __tablename__ = "regioes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    pedidos = db.relationship("Pedido", back_populates="regiao")


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    identificador = db.Column(db.String(20), unique=True, nullable=False)
    destinatario = db.Column(db.String(120), nullable=False)
    destino = db.Column(db.String(200), nullable=False)
    canal_venda = db.Column(db.String(50), nullable=False)
    descricao_volume = db.Column(db.String(240), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pendente")
    regiao_id = db.Column(db.Integer, db.ForeignKey("regioes.id"), nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    regiao = db.relationship("Regiao", back_populates="pedidos")
    acompanhamentos = db.relationship(
        "Acompanhamento",
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="Acompanhamento.criado_em.desc()",
    )
    ocorrencias = db.relationship(
        "Ocorrencia",
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="Ocorrencia.criado_em.desc()",
    )


class Acompanhamento(db.Model):
    __tablename__ = "acompanhamentos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    observacao = db.Column(db.String(240), nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    pedido = db.relationship("Pedido", back_populates="acompanhamentos")


class Ocorrencia(db.Model):
    __tablename__ = "ocorrencias"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    providencia = db.Column(db.String(500))
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    pedido = db.relationship("Pedido", back_populates="ocorrencias")


def seed_demo_data():
    regioes = {nome: Regiao(nome=nome) for nome in REGIOES}
    db.session.add_all(regioes.values())
    db.session.flush()

    pedidos = [
        Pedido(
            identificador="1001",
            destinatario="Cliente Exemplo A",
            destino="Rua das Flores, 120",
            regiao=regioes["Centro"],
            canal_venda="Loja virtual",
            descricao_volume="Caixa média - acessórios",
            status="Em andamento",
        ),
        Pedido(
            identificador="1002",
            destinatario="Cliente Exemplo B",
            destino="Avenida Norte, 450",
            regiao=regioes["Norte"],
            canal_venda="Marketplace",
            descricao_volume="Envelope - documentos fictícios",
            status="Entregue",
        ),
        Pedido(
            identificador="1003",
            destinatario="Cliente Exemplo C",
            destino="Rua do Sol, 88",
            regiao=regioes["Sul"],
            canal_venda="Loja virtual",
            descricao_volume="Caixa grande - itens domésticos",
            status="Devolvido",
        ),
    ]
    db.session.add_all(pedidos)
    db.session.flush()

    db.session.add_all(
        [
            Acompanhamento(
                pedido=pedidos[0],
                status="Pendente",
                observacao="Pedido recebido para separação.",
            ),
            Acompanhamento(
                pedido=pedidos[0],
                status="Em andamento",
                observacao="Pedido encaminhado para entrega.",
            ),
            Acompanhamento(
                pedido=pedidos[1],
                status="Pendente",
                observacao="Pedido recebido para separação.",
            ),
            Acompanhamento(
                pedido=pedidos[1],
                status="Entregue",
                observacao="Entrega confirmada no destino.",
            ),
            Acompanhamento(
                pedido=pedidos[2],
                status="Devolvido",
                observacao="Pedido retornou ao centro de distribuição.",
            ),
            Ocorrencia(
                pedido=pedidos[2],
                tipo="Devolução",
                descricao="Destinatário não localizado na tentativa de entrega.",
                providencia="Pedido direcionado para devolução ao centro.",
            ),
        ]
    )
    db.session.commit()
