-- ==============================================================
-- SORSABSA TRANSVERSAL: MESSAGING / BULK SENDER (v2.0)
-- ==============================================================

CREATE SCHEMA IF NOT EXISTS sorsabsa_messaging;

CREATE OR REPLACE FUNCTION sorsabsa_messaging.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Cola de envíos masivos (Migración desde SQLite)
CREATE TABLE sorsabsa_messaging.bulk_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,                    -- Para saber quién paga el envío
    telefono TEXT NOT NULL,
    nombre TEXT,
    mensaje_template TEXT,
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'enviado', 'fallido', 'reintentando')),
    intentos INTEGER DEFAULT 0,
    proximo_intento TIMESTAMPTZ DEFAULT now(),
    ultimo_error TEXT,
    fecha_envio TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TRIGGER update_bulk_queue_updated_at 
    BEFORE UPDATE ON sorsabsa_messaging.bulk_queue 
    FOR EACH ROW EXECUTE PROCEDURE sorsabsa_messaging.update_updated_at_column();