# database/models.py
"""
Modelos de base de datos para el sistema de administración de criptas
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from datetime import datetime
from typing import List, Optional

import shortuuid

def generar_cedula_automatica():
    """Generar cédula automática usando shortuuid"""
    return shortuuid.uuid()[:12].upper()

# Configuración de la base de datos
DATABASE_URL = "sqlite:///criptas.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Cliente(Base):
    __tablename__ = "clientes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    cedula: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    direccion: Mapped[Optional[str]] = mapped_column(Text)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relaciones
    ventas: Mapped[List["Venta"]] = relationship("Venta", back_populates="cliente")
    beneficiarios_titulares: Mapped[List["Beneficiario"]] = relationship(
        "Beneficiario", foreign_keys="Beneficiario.titular_id", back_populates="titular"
    )
    beneficiarios_como_beneficiario: Mapped[List["Beneficiario"]] = relationship(
        "Beneficiario", foreign_keys="Beneficiario.beneficiario_id", back_populates="beneficiario_persona"
    )
    
    def __init__(self, **kwargs):
        # Generar cédula automática si no se proporciona
        if 'cedula' not in kwargs or not kwargs['cedula']:
            kwargs['cedula'] = generar_cedula_automatica()
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"Cliente(id={self.id}, nombre='{self.nombre} {self.apellido}', cedula='{self.cedula}')"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Nicho(Base):
    __tablename__ = "nichos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    seccion: Mapped[str] = mapped_column(String(50), nullable=False)
    fila: Mapped[str] = mapped_column(String(10), nullable=False)
    columna: Mapped[str] = mapped_column(String(10), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relaciones
    ventas: Mapped[List["Venta"]] = relationship("Venta", back_populates="nicho")
    
    def __repr__(self):
        return f"Nicho(numero='{self.numero}', seccion='{self.seccion}', disponible={self.disponible})"

class Venta(Base):
    __tablename__ = "ventas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    numero_contrato: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    nicho_id: Mapped[int] = mapped_column(ForeignKey("nichos.id"), nullable=False)
    precio_total: Mapped[float] = mapped_column(Float, nullable=False)
    enganche: Mapped[float] = mapped_column(Float, default=0.0)
    saldo_restante: Mapped[float] = mapped_column(Float, nullable=False)
    tipo_pago: Mapped[str] = mapped_column(String(20), nullable=False)  # "contado" o "credito"
    pagado_completamente: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_venta: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    fecha_ultimo_pago: Mapped[Optional[datetime]] = mapped_column(DateTime)
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relaciones
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="ventas")
    nicho: Mapped["Nicho"] = relationship("Nicho", back_populates="ventas")
    pagos: Mapped[List["Pago"]] = relationship("Pago", back_populates="venta")
    beneficiarios: Mapped[List["Beneficiario"]] = relationship("Beneficiario", back_populates="venta")
    
    def __repr__(self):
        return f"Venta(contrato='{self.numero_contrato}', cliente_id={self.cliente_id}, nicho_id={self.nicho_id})"
    
    @property
    def total_pagado(self):
        return sum(pago.monto for pago in self.pagos) + self.enganche
    
    def actualizar_saldo(self):
        """Actualizar saldo restante basado en los pagos realizados"""
        self.saldo_restante = self.precio_total - self.total_pagado
        self.pagado_completamente = self.saldo_restante <= 0

class Pago(Base):
    __tablename__ = "pagos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False)
    numero_recibo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    metodo_pago: Mapped[str] = mapped_column(String(50), nullable=False)  # "efectivo", "transferencia", etc.
    concepto: Mapped[str] = mapped_column(String(200), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relaciones
    venta: Mapped["Venta"] = relationship("Venta", back_populates="pagos")
    
    def __repr__(self):
        return f"Pago(recibo='{self.numero_recibo}', monto={self.monto}, fecha={self.fecha_pago})"

class Beneficiario(Base):
    __tablename__ = "beneficiarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False)
    titular_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    beneficiario_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 o 2 (máximo 2 beneficiarios)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relaciones
    venta: Mapped["Venta"] = relationship("Venta", back_populates="beneficiarios")
    titular: Mapped["Cliente"] = relationship("Cliente", foreign_keys=[titular_id], back_populates="beneficiarios_titulares")
    beneficiario_persona: Mapped["Cliente"] = relationship("Cliente", foreign_keys=[beneficiario_id], back_populates="beneficiarios_como_beneficiario")
    
    def __repr__(self):
        return f"Beneficiario(venta_id={self.venta_id}, orden={self.orden}, activo={self.activo})"

# Funciones auxiliares para manejo de la base de datos
def get_db_session():
    """Obtener una nueva sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # No cerramos aquí, se debe cerrar manualmente

def crear_cliente_con_cedula_automatica(nombre, apellido, telefono=None, email=None, direccion=None):
    """Crear un nuevo cliente con cédula generada automáticamente"""
    db = get_db_session()
    try:
        cliente = Cliente(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            direccion=direccion
            # La cédula se genera automáticamente en el __init__
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def crear_nicho(numero, seccion, fila, columna, precio, descripcion=None):
    """Crear un nuevo nicho"""
    db = get_db_session()
    try:
        nicho = Nicho(
            numero=numero,
            seccion=seccion,
            fila=fila,
            columna=columna,
            precio=precio,
            descripcion=descripcion
        )
        db.add(nicho)
        db.commit()
        db.refresh(nicho)
        return nicho
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def buscar_nichos_disponibles():
    """Obtener todos los nichos disponibles"""
    db = get_db_session()
    try:
        return db.query(Nicho).filter(Nicho.disponible == True).all()
    finally:
        db.close()

def buscar_venta_por_contrato(numero_contrato):
    """Buscar venta por número de contrato"""
    db = get_db_session()
    try:
        return db.query(Venta).filter(Venta.numero_contrato == numero_contrato).first()
    finally:
        db.close()

def buscar_cliente_por_cedula(cedula):
    """Buscar cliente por número de cédula"""
    db = get_db_session()
    try:
        return db.query(Cliente).filter(Cliente.cedula == cedula).first()
    finally:
        db.close()

def generar_numero_contrato():
    """Generar número único de contrato"""
    db = get_db_session()
    try:
        # Obtener el último número de contrato
        ultima_venta = db.query(Venta).order_by(Venta.id.desc()).first()
        if ultima_venta:
            ultimo_numero = int(ultima_venta.numero_contrato.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        # Formato: CRIPTA-YYYY-NNNN
        year = datetime.now().year
        return f"CRIPTA-{year}-{nuevo_numero:04d}"
    finally:
        db.close()

def generar_numero_recibo():
    """Generar número único de recibo"""
    db = get_db_session()
    try:
        # Obtener el último número de recibo
        ultimo_pago = db.query(Pago).order_by(Pago.id.desc()).first()
        if ultimo_pago:
            ultimo_numero = int(ultimo_pago.numero_recibo.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        # Formato: REC-YYYY-NNNN
        year = datetime.now().year
        return f"REC-{year}-{nuevo_numero:04d}"
    finally:
        db.close()