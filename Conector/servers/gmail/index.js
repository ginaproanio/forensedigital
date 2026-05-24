#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";

/**
 * SORSABSA - Conector Hub - Gmail Server
 * Centraliza la comunicación formal del ecosistema.
 */

const oauth2Client = new google.auth.OAuth2(
  process.env.GMAIL_CLIENT_ID,
  process.env.GMAIL_CLIENT_SECRET
);

oauth2Client.setCredentials({
  refresh_token: process.env.GMAIL_REFRESH_TOKEN
});

const gmail = google.gmail({ version: "v1", auth: oauth2Client });

const server = new Server(
  {
    name: "sorsabsa-gmail",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "send_formal_email",
        description: "Envía un correo formal. Útil para actas de CondoManager o notificaciones de LegalConnect.",
        inputSchema: {
          type: "object",
          properties: {
            to: { type: "string" },
            subject: { type: "string" },
            body: { type: "string", description: "Soporta HTML" },
            tenant_id: { type: "string", description: "ID del estudio jurídico o condominio solicitante" }
          },
          required: ["to", "subject", "body"],
        },
      },
      {
        name: "send_condomanager_statement",
        description: "Envía el estado de cuenta mensual a un residente de CondoManager con formato profesional.",
        inputSchema: {
          type: "object",
          properties: {
            to: { type: "string" },
            resident_name: { type: "string" },
            condominium_name: { type: "string" },
            unit_identifier: { type: "string" },
            period: { type: "string", description: "Mes y Año (ej: Mayo 2026)" },
            total_amount: { type: "number" },
            details_html: { type: "string", description: "Tabla HTML con el desglose de rubros" },
            tenant_id: { type: "string" }
          },
          required: ["to", "resident_name", "condominium_name", "unit_identifier", "period", "total_amount", "details_html", "tenant_id"],
        },
      },
      {
        name: "search_legal_notifications",
        description: "Busca correos en la bandeja de entrada relacionados con términos legales.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string" },
            maxResults: { type: "number", default: 5 },
          },
          required: ["query"],
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "send_formal_email") {
      const emailLines = [
        'Content-Type: text/html; charset="UTF-8"\n',
        'MIME-Version: 1.0\n',
        'Content-Transfer-Encoding: 7bit\n',
        `to: ${args.to}\n`,
        `subject: ${args.subject}\n\n`,
        args.body
      ].join('');

      const encodedMail = Buffer.from(emailLines).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');
      
      const res = await gmail.users.messages.send({
        userId: 'me',
        requestBody: { raw: encodedMail }
      });

      // Log en consola para que Docker capture el evento (Auditoría básica)
      console.error(`[AUDIT] Email enviado para Tenant: ${args.tenant_id || 'Global'}. MsgID: ${res.data.id}`);

      return { content: [{ type: "text", text: `Email enviado. ID: ${res.data.id}` }] };
    }

    if (name === "send_condomanager_statement") {
      const { to, resident_name, condominium_name, unit_identifier, period, total_amount, details_html, tenant_id } = args;
      
      const emailBody = `
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 30px; color: #1a202c;">
          <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #2b6cb0; margin: 0;">${condominium_name}</h1>
            <p style="color: #718096; text-transform: uppercase; font-size: 14px; letter-spacing: 1px;">Estado de Cuenta Mensual</p>
          </div>
          <hr style="border: 0; border-top: 1px solid #edf2f7; margin: 20px 0;">
          <p>Estimado(a) <strong>${resident_name}</strong>,</p>
          <p>Se adjunta el resumen de sus obligaciones correspondientes a la unidad <strong>${unit_identifier}</strong> para el periodo de <strong>${period}</strong>.</p>
          
          <div style="margin: 25px 0;">
            ${details_html}
          </div>
          
          <div style="background-color: #ebf8ff; padding: 20px; border-radius: 6px; text-align: right; border: 1px solid #bee3f8;">
            <span style="font-size: 14px; color: #2c5282;">VALOR TOTAL A PAGAR:</span><br>
            <span style="font-size: 24px; font-weight: bold; color: #2b6cb0;">$${total_amount.toFixed(2)}</span>
          </div>
          
          <p style="font-size: 12px; color: #a0aec0; margin-top: 40px; text-align: center; line-height: 1.5;">
            Este es un documento oficial generado por la administración a través de <strong>SORSABSA - CondoManager Hub</strong>.<br>
            Por favor, asegúrese de realizar su pago antes de la fecha de vencimiento para evitar intereses de mora.
          </p>
        </div>
      `;

      const emailLines = [
        'Content-Type: text/html; charset="UTF-8"\n',
        'MIME-Version: 1.0\n',
        'Content-Transfer-Encoding: 7bit\n',
        `to: ${to}\n`,
        `subject: 📑 Estado de Cuenta ${period} - ${condominium_name} (${unit_identifier})\n\n`,
        emailBody
      ].join('');

      const encodedMail = Buffer.from(emailLines).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');
      
      const res = await gmail.users.messages.send({ userId: 'me', requestBody: { raw: encodedMail } });
      console.error(`[AUDIT] Statement enviado | Tenant: ${tenant_id} | Unit: ${unit_identifier} | ID: ${res.data.id}`);
      return { content: [{ type: "text", text: `Estado de cuenta enviado exitosamente a ${to}.` }] };
    }

    if (name === "search_legal_notifications") {
      const res = await gmail.users.messages.list({
        userId: 'me',
        q: args.query,
        maxResults: args.maxResults
      });

      const messages = res.data.messages || [];
      return { content: [{ type: "text", text: `Se encontraron ${messages.length} hilos de correo.` }] };
    }

    throw new Error(`Herramienta ${name} no implementada`);
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error en Hub Gmail: ${error.message}` }],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
main().catch(console.error);