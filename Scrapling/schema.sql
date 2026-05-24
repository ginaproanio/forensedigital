-- ==============================================================
-- SORSABSA TRANSVERSAL: SCrapling (v2.0)
-- ==============================================================

CREATE SCHEMA IF NOT EXISTS sorsabsa_scrapling;

-- Función para actualizar el timestamp
CREATE OR REPLACE FUNCTION sorsabsa_scrapling.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Tabla de Prospectos (Leads): Abogados y estudios jurídicos detectados
CREATE TABLE sorsabsa_scrapling.prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_estudio TEXT NOT NULL,
    contacto_principal TEXT,
    telefono TEXT,
    email TEXT UNIQUE,
    direccion TEXT,
    provincia TEXT, -- Pichincha, Guayas, etc.
    fuente TEXT DEFAULT 'google_maps',
    calidad_lead TEXT DEFAULT 'media' CHECK (calidad_lead IN ('baja', 'media', 'alta', 'premium', 'vip')),
    metadata JSONB DEFAULT '{}', -- { "website": "...", "rating": 4.5 }
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TRIGGER update_prospects_updated_at 
    BEFORE UPDATE ON sorsabsa_scrapling.prospects 
    FOR EACH ROW EXECUTE PROCEDURE sorsabsa_scrapling.update_updated_at_column();

-- Registro de ejecuciones de raspado
CREATE TABLE sorsabsa_scrapling.extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_query TEXT NOT NULL, -- ej: 'abogados en quito'
    status TEXT DEFAULT 'running',
    leads_found INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
