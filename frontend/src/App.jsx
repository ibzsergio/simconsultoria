import { useEffect, useState } from "react";

const MSG_EXITO = "mensaje enviado";
const MSG_EXITO_MS = 4500;

/** Desarrollo: VITE_API_URL opcional (p. ej. API remota); si vacío → proxy Vite `/api`. Producción Netlify → siempre mismo origen (`/api/...`; rewrite en netlify.toml → Railway). */
const API_BASE = import.meta.env.PROD
  ? ""
  : String(import.meta.env.VITE_API_URL ?? "")
      .trim()
      .replace(/\/+$/, "");

function mensajeErrorApi(res, cuerpoCrudo) {
  const raw = (cuerpoCrudo || "").trim();
  if (!raw) {
    return `Respuesta HTTP ${res.status} sin cuerpo. Revisa la terminal del servidor Django.`;
  }
  if (raw.startsWith("<!") || raw.startsWith("<html") || raw.startsWith("<")) {
    return `El servidor devolvió HTML en lugar de JSON (HTTP ${res.status}). Revisa la terminal de Django.`;
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    return raw.length > 400 ? `${raw.slice(0, 400)}…` : raw;
  }
  if (data && typeof data === "object") {
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map(String).join(" ");
    const campos = Object.entries(data).filter(([k]) => k !== "detail");
    if (campos.length > 0) {
      return campos
        .map(([campo, val]) => {
          if (Array.isArray(val)) return `${campo}: ${val.join(" ")}`;
          if (val && typeof val === "object") return `${campo}: ${JSON.stringify(val)}`;
          return `${campo}: ${val}`;
        })
        .join(" · ");
    }
    if (data.detail != null) return JSON.stringify(data.detail);
  }
  return `HTTP ${res.status}`;
}

const GALLERY_SRC = [
  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=640&q=80",
  "https://images.unsplash.com/photo-1551434678-e076c223a692?w=640&q=80",
  "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=640&q=80",
  "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=640&q=80",
  "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=640&q=80",
  "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640&q=80",
];

export default function App() {
  const [formMsg, setFormMsg] = useState({ show: false, text: "", variant: "ok" });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (!formMsg.show || formMsg.variant !== "success") return undefined;
    const t = window.setTimeout(() => {
      setFormMsg({ show: false, text: "", variant: "ok" });
    }, MSG_EXITO_MS);
    return () => window.clearTimeout(t);
  }, [formMsg.show, formMsg.variant]);

  async function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    const body = {
      nombre: (fd.get("nombre") || "").toString().trim(),
      correo: (fd.get("correo") || "").toString().trim(),
      telefono: (fd.get("telefono") || "").toString().trim(),
      tema: (fd.get("tema") || "").toString(),
      mensaje: (fd.get("mensaje") || "").toString().trim(),
    };
    setSending(true);
    setFormMsg({ show: false, text: "", variant: "ok" });
    try {
      const base = (API_BASE || "").replace(/\/+$/, "");
      const urlContacto = base ? `${base}/api/contacto/` : "/api/contacto/";
      const res = await fetch(urlContacto, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(body),
      });
      const cuerpoCrudo = await res.text();
      if (!res.ok) {
        setFormMsg({
          show: true,
          variant: "err",
          text: `No se pudo guardar el mensaje. ${mensajeErrorApi(res, cuerpoCrudo)}`,
        });
        return;
      }
      form.reset();
      setFormMsg({ show: true, variant: "success", text: MSG_EXITO });
    } catch (err) {
      const detalle =
        err instanceof TypeError
          ? err.message
          : err instanceof Error
            ? err.message
            : String(err);
      setFormMsg({
        show: true,
        variant: "err",
        text: import.meta.env.DEV
          ? `No se pudo conectar con la API (${detalle}). ¿Corre django en :8000 y tienes VITE_API_PROXY_TARGET en vite.config?`
          : `No se pudo enviar (${detalle}). Revisa que el sitio en Netlify esté desplegado con el último build y que el backend en Railway siga Online.`,
      });
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <header className="site-header" role="banner">
        <div className="nav-inner">
          <p className="brand">
            <a href="#inicio">
              <span>SIM</span> Consultoría
            </a>
          </p>
          <nav className="site-nav" aria-label="Principal">
            <ul>
              <li>
                <a href="#inicio">Inicio</a>
              </li>
              <li>
                <a href="#sobre-nosotros">Sobre nosotros</a>
              </li>
              <li>
                <a href="#mision-vision">Misión y visión</a>
              </li>
              <li>
                <a href="#servicios">Servicios</a>
              </li>
              <li>
                <a href="#clientes">Clientes</a>
              </li>
              <li>
                <a href="#galeria">Galería</a>
              </li>
              <li>
                <a href="#multimedia">Multimedia</a>
              </li>
              <li>
                <a href="#testimonios">Testimonios</a>
              </li>
              <li>
                <a href="#contacto">Contacto</a>
              </li>
              <li>
                <a href="#redes">Redes</a>
              </li>
              <li>
                <a href="#enlaces-externos">Enlaces</a>
              </li>
              <li>
                <a href="#privacidad">Privacidad</a>
              </li>
              <li>
                <a href="#terminos">Términos</a>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      <main id="contenido">
        <section id="inicio" className="wrap hero" aria-labelledby="titulo-inicio">
          <div>
            <p className="eyebrow">Consultoría informática en México</p>
            <h1 id="titulo-inicio">SIM — tecnología al servicio de tu organización</h1>
            <p className="lead">
              Acompañamos a empresas e instituciones en{" "}
              <strong>arquitectura TI, desarrollo, datos y ciberseguridad</strong>, con enfoque práctico y alineación a
              la normativa mexicana aplicable. Explora las secciones o escríbenos desde el formulario de contacto.
            </p>
            <div className="btn-row">
              <a className="btn btn-primary" href="#servicios">
                Servicios y productos
              </a>
              <a className="btn btn-ghost" href="#contacto">
                Contacto
              </a>
            </div>
          </div>
          <div className="hero-visual">
            <img
              src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=900&auto=format&fit=crop"
              width="560"
              height="380"
              alt="Visualización abstracta de redes y datos digitales"
              loading="eager"
            />
          </div>
        </section>

        <section id="sobre-nosotros" className="wrap">
          <h2>Sobre nosotros</h2>
          <p className="section-desc">Consultores que conectan negocio, operación y equipos técnicos.</p>
          <div className="card">
            <p>
              <strong>SIM</strong> es una consultora de informática de vocación generalista: integramos visión de
              infraestructura, aplicaciones y seguridad para que las decisiones de inversión tecnológica sean
              comprensibles para la dirección y sostenibles para el equipo interno.
            </p>
            <p>
              Trabajamos con organizaciones en distintos tamaños y sectores en México, priorizando documentación clara,
              transferencia de conocimiento y criterios de cumplimiento (por ejemplo <strong>LFPDPPP</strong> y
              lineamientos federales en ciberseguridad cuando el proyecto lo requiere).
            </p>
          </div>
        </section>

        <section id="mision-vision" className="wrap">
          <h2>Misión y visión</h2>
          <div className="grid-two">
            <div className="card">
              <h3>Misión</h3>
              <p>
                Ofrecer consultoría informática rigurosa y cercana que traduzca necesidades de negocio en soluciones
                técnicas viables, seguras y mantenibles, sin depender de jerga innecesaria ni de dependencias
                tecnológicas impuestas.
              </p>
            </div>
            <div className="card">
              <h3>Visión</h3>
              <p>
                Ser un socio de referencia en México para la modernización digital responsable: organizaciones que
                confían en SIM para planificar, ejecutar y operar sus sistemas con autonomía creciente y resiliencia
                frente a amenazas.
              </p>
            </div>
          </div>
        </section>

        <section id="servicios" className="wrap">
          <h2>Servicios y productos</h2>
          <p className="section-desc">
            Líneas de consultoría y paquetes reutilizables que adaptamos a tu contexto.
          </p>
          <ul className="info-list block-mb">
            <li>
              <strong>Arquitectura y estrategia TI:</strong> inventario, hoja de ruta, nube híbrida y modernización.
            </li>
            <li>
              <strong>Desarrollo e integraciones:</strong> APIs, calidad de software, revisiones técnicas.
            </li>
            <li>
              <strong>Infraestructura y operaciones:</strong> respaldo, redes, continuidad del negocio.
            </li>
            <li>
              <strong>Datos y analítica:</strong> modelos, gobierno del dato, preparación para IA aplicada.
            </li>
            <li>
              <strong>Ciberseguridad:</strong> riesgos, endurecimiento, concienciación y coordinación con áreas legales.
            </li>
          </ul>
          <p className="section-desc table-caption">Resumen breve de los tres productos:</p>
          <div className="table-wrap" role="region" aria-label="Resumen de paquetes">
            <table className="sim-table">
              <thead>
                <tr>
                  <th scope="col">Producto</th>
                  <th scope="col">Plazo típico</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Diagnóstico</td>
                  <td>3–5 semanas</td>
                </tr>
                <tr>
                  <td>Suscripción asesoría</td>
                  <td>Por meses</td>
                </tr>
                <tr>
                  <td>Acompañamiento proyecto</td>
                  <td>Según proyecto</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="grid-three">
            <article className="card">
              <h3>Paquete diagnóstico</h3>
              <p className="small">
                Entrevistas, inventario breve y informe ejecutivo con prioridades a 90 días.
              </p>
            </article>
            <article className="card">
              <h3>Suscripción asesoría</h3>
              <p className="small">Horas mensuales para comités TI, revisión de proveedores y dudas puntuales.</p>
            </article>
            <article className="card">
              <h3>Acompañamiento proyecto</h3>
              <p className="small">Seguimiento de hitos, riesgos y calidad en implementaciones críticas.</p>
            </article>
          </div>
        </section>

        <section id="clientes" className="wrap">
          <h2>Clientes y aliados estratégicos</h2>
          <p className="section-desc">
            Organizaciones con las que hemos colaborado o mantenemos alianzas de servicio.
          </p>
          <div className="clients">
            <span>Logística del Bajío</span>
            <span>Salud Integral del Sureste</span>
            <span>Cooperativa Financiera Regional</span>
            <span>Universidad tecnológica aliada</span>
            <span>Distribuidor de nube nacional</span>
          </div>
        </section>

        <section id="galeria" className="wrap">
          <h2>Galería / portafolio</h2>
          <p className="section-desc">Imágenes de referencia que ilustran nuestro ámbito de trabajo.</p>
          <div className="gallery" role="group" aria-label="Galería ilustrativa">
            {GALLERY_SRC.map((src, idx) => (
              <figure key={src}>
                <img
                  src={src}
                  alt={`Proyecto y entorno de trabajo tecnológico, imagen ${idx + 1} del portafolio ilustrativo`}
                  loading="lazy"
                  width="400"
                  height="260"
                />
              </figure>
            ))}
          </div>
        </section>

        <section id="multimedia" className="wrap" aria-labelledby="titulo-iframe">
          <h2 id="titulo-iframe">Ingram Micro México | ¿Te apasiona la innovación tecnológica?</h2>
          <div className="video-wrap">
            <iframe
              title="Ingram Micro México — ¿Te apasiona la innovación tecnológica? (YouTube)"
              width="560"
              height="315"
              src="https://www.youtube-nocookie.com/embed/ae73uSQdfTc"
              loading="lazy"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>
        </section>

        <section id="testimonios" className="wrap">
          <h2>Testimonios / casos de éxito</h2>
          <div className="grid-two">
            <blockquote className="quote card">
              El diagnóstico de SIM nos permitió unificar tres proveedores en una arquitectura coherente; en seis meses
              redujimos incidentes operativos repetitivos.
              <cite>— Dirección de TI, sector logística (México)</cite>
            </blockquote>
            <blockquote className="quote card">
              La parte legal valoró que el informe de tratamiento de datos fuera entendible y accionable; el equipo
              técnico pudo implementar sin fricción.
              <cite>— Responsable de cumplimiento, servicios financieros</cite>
            </blockquote>
          </div>
        </section>

        <section id="contacto" className="wrap">
          <h2>Contacto</h2>
          <div
            className={`msg${formMsg.show ? ` show ${formMsg.variant}` : ""}`}
            role="status"
            aria-live="polite"
          >
            {formMsg.text}
          </div>
          <form className="contact-form" action="#" method="post" autoComplete="on" onSubmit={handleFormSubmit}>
            <div>
              <label htmlFor="nombre">Nombre completo</label>
              <input id="nombre" name="nombre" type="text" required maxLength={120} disabled={sending} />
            </div>
            <div>
              <label htmlFor="correo">Correo electrónico</label>
              <input id="correo" name="correo" type="email" required disabled={sending} />
            </div>
            <div>
              <label htmlFor="telefono">Teléfono</label>
              <input id="telefono" name="telefono" type="tel" maxLength={40} disabled={sending} />
            </div>
            <div>
              <label htmlFor="tema">Tema</label>
              <select id="tema" name="tema" required defaultValue="" disabled={sending}>
                <option value="">Selecciona…</option>
                <option value="Consultoría general">Consultoría general</option>
                <option value="Ciberseguridad">Ciberseguridad</option>
                <option value="Desarrollo / integraciones">Desarrollo / integraciones</option>
                <option value="Otro">Otro</option>
              </select>
            </div>
            <div>
              <label htmlFor="mensaje">Mensaje</label>
              <textarea id="mensaje" name="mensaje" required disabled={sending} />
            </div>
            <button type="submit" className="btn btn-primary" id="send-btn" disabled={sending}>
              {sending ? "Enviando…" : "Enviar"}
            </button>
          </form>
        </section>

        <section id="enlaces-externos" className="wrap">
          <h2>Enlaces de interés</h2>
          <p className="section-desc">Sitios oficiales de referencia en México.</p>
          <ul className="info-list">
            <li>
              <a href="https://www.gob.mx/atdt" target="_blank" rel="noopener noreferrer">
                ATDT (gob.mx)
              </a>{" "}
              — transformación digital y telecomunicaciones.
            </li>
            <li>
              <a href="https://www.gob.mx/atdt/agendas/ciberseguridad" target="_blank" rel="noopener noreferrer">
                ATDT — Ciberseguridad
              </a>{" "}
              — agenda federal.
            </li>
          </ul>
        </section>
      </main>

      <footer className="site-footer" role="contentinfo">
        <div className="wrap legal-grid">
          <div className="card" id="privacidad">
            <h2>Aviso de privacidad</h2>
            <p className="small">
              Los datos del formulario de contacto se tratan conforme a la <strong>LFPDPPP</strong> y al aviso de
              privacidad de SIM. Se utilizan para responder tu solicitud y para enviarte el correo de confirmación al
              mismo correo que indiques.
            </p>
          </div>
          <div className="card" id="terminos">
            <h2>Términos legales</h2>
            <p className="small">
              El contenido de este sitio es informativo. Las recomendaciones de consultoría se formalizan en contratos
              y propuestas por escrito. SIM no garantiza disponibilidad continua de enlaces a sitios de terceros.
            </p>
          </div>
        </div>

        <div className="footer-ribbon">
          <div className="wrap footer-ribbon-inner">
            <nav id="redes" className="footer-social-icons" aria-label="Redes sociales">
              <a
                href="https://www.facebook.com/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Facebook"
              >
                <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
                  />
                </svg>
              </a>
              <a
                href="https://www.instagram.com/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Instagram"
              >
                <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"
                  />
                </svg>
              </a>
              <a
                href="https://www.linkedin.com/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
              >
                <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
                  />
                </svg>
              </a>
              <a href="https://github.com/" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
                  />
                </svg>
              </a>
            </nav>
            <p className="footer-copyright">
              © {new Date().getFullYear()} SIM Consultoría — Todos los derechos reservados
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
