#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import bizSdk from 'facebook-nodejs-business-sdk';
import crypto from 'crypto';

/**
 * SORSABSA - Conector Hub - Meta Ads Server
 * Especializado en gestión de campañas y audiencias de Scrapling.
 */

const AdsSdk = bizSdk.FacebookAdsApi;
const accessToken = process.env.META_ACCESS_TOKEN;
const adAccountId = process.env.META_AD_ACCOUNT_ID;

if (!accessToken || !adAccountId) {
  console.error("Faltan credenciales META_ACCESS_TOKEN o META_AD_ACCOUNT_ID");
  process.exit(1);
}

AdsSdk.init(accessToken);
const account = new bizSdk.AdAccount(adAccountId.startsWith('act_') ? adAccountId : `act_${adAccountId}`);

const hashData = (val) => crypto.createHash('sha256').update(val.trim().toLowerCase()).digest('hex');

const server = new Server(
  { name: "sorsabsa-meta", version: "1.1.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_ad_kpis",
        description: "Obtiene KPIs de rendimiento (gasto, clics, conversiones).",
        inputSchema: {
          type: "object",
          properties: { date_preset: { type: "string", default: "last_30d" } }
        }
      },
      {
        name: "create_custom_audience",
        description: "Crea una Audiencia Personalizada en Meta Ads. Ideal para agrupar prospectos extraídos por Scrapling.",
        inputSchema: {
          type: "object",
          properties: {
            name: { type: "string" },
            description: { type: "string" },
            tenant_id: { type: "string", description: "ID del solicitante para auditoría" }
          },
          required: ["name"]
        }
      },
      {
        name: "upload_leads_to_audience",
        description: "Sube una lista de emails o teléfonos a una audiencia. Los datos se hashean automáticamente.",
        inputSchema: {
          type: "object",
          properties: {
            audience_id: { type: "string" },
            emails: { type: "array", items: { type: "string" } },
            phones: { type: "array", items: { type: "string" } }
          },
          required: ["audience_id"]
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "get_ad_kpis") {
      const insights = await account.getInsights(
        ['spend', 'impressions', 'clicks', 'ctr', 'conversions'],
        { date_preset: args.date_preset || 'last_30d' }
      );
      return { content: [{ type: "text", text: JSON.stringify(insights.map(i => i._data)) }] };
    }

    if (name === "create_custom_audience") {
      const audience = await account.createCustomAudience(
        [],
        {
          name: args.name,
          subtype: 'CUSTOM',
          description: args.description || 'Creada vía SORSABSA Hub',
          customer_file_source: 'USER_PROVIDED_ONLY'
        }
      );
      
      console.error(`[AUDIT] Custom Audience creada: ${args.name} para Tenant: ${args.tenant_id || 'Global'}`);
      
      return { content: [{ type: "text", text: `Audiencia creada con ID: ${audience.id}` }] };
    }

    if (name === "upload_leads_to_audience") {
      const audience = new bizSdk.CustomAudience(args.audience_id);
      const schema = [];
      const data = [];

      if (args.emails && args.emails.length > 0) {
        schema.push('EMAIL');
        args.emails.forEach(e => data.push([hashData(e)]));
      } else if (args.phones && args.phones.length > 0) {
        schema.push('PHONE');
        args.phones.forEach(p => data.push([hashData(p)]));
      }

      if (data.length === 0) throw new Error("No hay datos para subir.");

      await audience.createUser(
        [],
        {
          payload: {
            schema: schema,
            data: data
          }
        }
      );

      console.error(`[AUDIT] Leads cargados a audiencia: ${args.audience_id}. Cantidad: ${data.length}`);

      return { content: [{ type: "text", text: `Se han subido ${data.length} registros a la audiencia.` }] };
    }

    throw new Error(`Herramienta ${name} no disponible.`);
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error en Meta SDK: ${error.message}` }],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
main().catch(console.error);