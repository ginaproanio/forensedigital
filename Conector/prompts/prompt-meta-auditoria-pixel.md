# Prompt: Auditoría de Pixel/Dataset Meta (Solo Lectura)

Copiar/pegar:

```text
Eres mi auditor de tracking de Meta. Tienes acceso al CLI oficial de Meta Ads (Ads CLI).

Cuenta de Meta: act_[ID_DE_MI_AD_ACCOUNT]
Dataset/Pixel ID: [DATASET_ID]
Catálogo conectado: [CATALOG_ID o "ninguno"]

Tareas:
1) Lista campañas activas con `meta ads campaign list`.
2) Valida que el dataset [DATASET_ID] esté conectado a la cuenta (sin modificar).
3) Confirma si hay conversiones/eventos en insights.
4) Genera reporte con:
   - (a) Estado del pixel (verde/amarillo/rojo)
   - (b) Campañas que no aprovechan pixel
   - (c) Eventos faltantes o mal configurados
   - (d) Acciones de reparación recomendadas

Reglas:
- NO crees/modifiques/borres nada.
- Solo lectura y diagnóstico.
- Una llamada al CLI a la vez.
```

## Checklist de auditoría

### 1. Verificación de conexión
- [ ] Pixel/Dataset está activo
- [ ] Conectado a la cuenta de anuncios correcta
- [ ] Permisos adecuados configurados

### 2. Eventos de conversión
- [ ] Purchase
- [ ] AddToCart
- [ ] InitiateCheckout
- [ ] Lead
- [ ] CompleteRegistration
- [ ] ViewContent
- [ ] Search
- [ ] AddPaymentInfo

### 3. Configuración de campañas
- [ ] Campañas usando optimización de conversiones
- [ ] Pixel seleccionado correctamente
- [ ] Eventos de conversión bien definidos

### 4. Catálogo (si aplica)
- [ ] Catálogo conectado al dataset
- [ ] Productos sincronizados
- [ ] Eventos de catálogo activos

## Comandos útiles de auditoría

```bash
# Listar campañas activas
meta ads campaign list --status ACTIVE

# Ver insights con conversiones
meta ads insights get --date-preset last_7d --fields conversions,cost_per_action_type

# Validar configuración de pixel (si está disponible en CLI)
meta ads pixel validate --pixel-id [PIXEL_ID]
```

## Interpretación del semáforo

- 🟢 **Verde**: Pixel funcionando correctamente, todas las conversiones trackeadas
- 🟡 **Amarillo**: Pixel activo pero con problemas menores (eventos faltantes, configuración subóptima)
- 🔴 **Rojo**: Pixel inactivo, desconectado o con errores críticos de tracking