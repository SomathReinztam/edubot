import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { streamAnalysis } from '../api.js'
import { useUser } from '../App.jsx'
import Layout from '../components/Layout.jsx'
import MarkdownRenderer from '../components/MarkdownRenderer.jsx'

// ── Model catalog ────────────────────────────────────────
const MODELS = {
  google:   ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'gemini-3.1-pro-preview'],
  groq:     ['llama-3.3-70b-versatile', 'openai/gpt-oss-120b', 'moonshotai/kimi-k2-instruct-0905'],
  deepseek: ['deepseek-chat', 'deepseek-reasoner'],
}

const NODE_ROLE = {
  initial_deep_query_node: 'analyst',
  deep_query_node:         'analyst',
  querier_ReAct_node:      'querier',
  tool_node_wrapper:       'tool',
  should_end_node:         'default',
  set_ReAct_messages_node: 'default',
  clear_ReAct_messages_node: 'default',
}

// ── ModelCard sub-component ──────────────────────────────
function ModelCard({ title, value, onChange }) {
  return (
    <div className="model-card">
      <div className="model-card-title">{title}</div>
      <div className="form-group">
        <label className="form-label">Proveedor</label>
        <select
          className="form-select"
          value={value.client}
          onChange={e => onChange({ ...value, client: e.target.value, model: MODELS[e.target.value][0] })}
        >
          <option value="google">Google</option>
          <option value="groq">Groq</option>
          <option value="deepseek">DeepSeek</option>
        </select>
      </div>
      <div className="form-group">
        <label className="form-label">Modelo</label>
        <select
          className="form-select"
          value={value.model}
          onChange={e => onChange({ ...value, model: e.target.value })}
        >
          {MODELS[value.client].map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label className="form-label">Temperatura: {value.temperature}</label>
        <input
          type="range" min="0" max="1" step="0.05"
          value={value.temperature}
          onChange={e => onChange({ ...value, temperature: parseFloat(e.target.value) })}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  )
}

// ── ThinkingStep sub-component ───────────────────────────
function ThinkingStep({ step, isLast, isStreaming }) {
  const role = NODE_ROLE[step.node] || 'default'
  const d = step.data

  const tokenInfo = d.input_tokens != null
    ? `${d.input_tokens} in · ${d.output_tokens} out · ${d.api_calls} calls`
    : null

  return (
    <details className="step" data-role={role} open={isLast}>
      <summary>
        <span className="step-label">{step.label}</span>
        {isLast && isStreaming
          ? <span className="step-loading">procesando…</span>
          : tokenInfo && <span className="step-tokens">{tokenInfo}</span>
        }
      </summary>
      <div className="step-content">
        {/* Analyst messages */}
        {d.analyst_messages?.map((msg, i) => (
          <div key={i} className="step-section">
            <div className="step-section-label">{msg.type}</div>
            <MarkdownRenderer content={msg.content} />
          </div>
        ))}

        {/* ReAct messages */}
        {d.react_messages?.map((msg, i) => (
          <div key={i} className="step-section">
            <div className="step-section-label">{msg.tool_name ? `Resultado: ${msg.tool_name}` : msg.type}</div>
            {msg.tool_calls?.map((tc, j) => (
              <div key={j} className="tool-call">
                <strong>{tc.name}</strong>({tc.args})
              </div>
            ))}
            {msg.content && !msg.tool_calls && (
              <div className="tool-result">{msg.content}</div>
            )}
            {msg.content && msg.tool_name && (
              <div className="tool-result">{msg.content}</div>
            )}
          </div>
        ))}

        {/* Should-end verdict */}
        {d.should_end && (
          <div className="step-section">
            {d.should_end.query && <span className="badge badge-blue">Necesita más datos</span>}
            {d.should_end.analysis && <span className="badge badge-green">Análisis listo</span>}
          </div>
        )}
      </div>
    </details>
  )
}

// ── Main page ─────────────────────────────────────────────
export default function NewAnalysis() {
  const { user } = useUser()
  const navigate = useNavigate()

  // Persist API keys in localStorage
  const [apiKeys, setApiKeys] = useState(() => {
    try { return JSON.parse(localStorage.getItem('edubot_api_keys')) || { google: '', groq: '', deepseek: '' } }
    catch { return { google: '', groq: '', deepseek: '' } }
  })

  const [models, setModels] = useState({
    analyst: { client: 'google', model: 'gemini-2.0-flash', temperature: 0.5 },
    querier: { client: 'groq',   model: 'openai/gpt-oss-120b', temperature: 0.1 },
    halting: { client: 'groq',   model: 'openai/gpt-oss-120b', temperature: 0.1 },
  })

  const [query, setQuery] = useState('')
  const [topN, setTopN] = useState(15)

  const [phase, setPhase] = useState('form') // form | streaming | done | error
  const [steps, setSteps] = useState([])
  const [finalAnalysis, setFinalAnalysis] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  const stepsEndRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('edubot_api_keys', JSON.stringify(apiKeys))
  }, [apiKeys])

  useEffect(() => {
    stepsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [steps])

  async function handleSubmit(e) {
    e.preventDefault()
    setPhase('streaming')
    setSteps([])
    setFinalAnalysis(null)
    setErrorMsg('')

    const makeModel = (role) => ({
      client: models[role].client,
      model: models[role].model,
      temperature: models[role].temperature,
      api_key: apiKeys[models[role].client],
    })

    const payload = {
      user_id: user.user_id,
      query,
      top_n: topN,
      model_analyst: makeModel('analyst'),
      model_querier: makeModel('querier'),
      model_halting: makeModel('halting'),
    }

    try {
      await streamAnalysis(payload, (event) => {
        if (event.type === 'node_update') {
          setSteps(prev => [...prev, event])
        } else if (event.type === 'complete') {
          setFinalAnalysis(event.data)
          setPhase('done')
        } else if (event.type === 'error') {
          setErrorMsg(event.data?.message || 'Error desconocido')
          setPhase('error')
        }
      })
    } catch (err) {
      setErrorMsg(err.message)
      setPhase('error')
    }
  }

  // ── Form phase ───────────────────────────────────────────
  if (phase === 'form') {
    return (
      <Layout>
        <div className="page-header">
          <h1 className="page-title">Nuevo análisis</h1>
          <Link to="/dashboard" className="btn btn-secondary btn-sm">← Dashboard</Link>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="card mb-4">
            <div className="card-title">Consulta</div>
            <div className="form-group">
              <label className="form-label">
                ¿Qué quieres analizar de la base de datos EduBot?
              </label>
              <textarea
                className="form-textarea"
                style={{ minHeight: 120 }}
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Ej: ¿Cuál es el estado de los proyectos en construcción?"
                required
              />
            </div>
            <div className="form-group" style={{ maxWidth: 200 }}>
              <label className="form-label">Máximo de filas por consulta SQL</label>
              <input
                className="form-input"
                type="number"
                min="5" max="100"
                value={topN}
                onChange={e => setTopN(parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-title">API Keys</div>
            <div className="model-grid">
              {['google', 'groq', 'deepseek'].map(provider => (
                <div key={provider} className="form-group">
                  <label className="form-label" style={{ textTransform: 'capitalize' }}>
                    {provider}
                  </label>
                  <input
                    className="form-input"
                    type="password"
                    value={apiKeys[provider]}
                    onChange={e => setApiKeys(k => ({ ...k, [provider]: e.target.value }))}
                    placeholder={`${provider} API key`}
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-title">Configuración de modelos</div>
            <div className="model-grid">
              {['analyst', 'querier', 'halting'].map(role => (
                <ModelCard
                  key={role}
                  title={role === 'analyst' ? 'Analista' : role === 'querier' ? 'Agente SQL' : 'Evaluador'}
                  value={models[role]}
                  onChange={v => setModels(m => ({ ...m, [role]: v }))}
                />
              ))}
            </div>
          </div>

          <button className="btn btn-primary" type="submit">
            Generar análisis
          </button>
        </form>
      </Layout>
    )
  }

  // ── Streaming / done / error phases ─────────────────────
  return (
    <Layout wide>
      <div className="page-header">
        <h1 className="page-title">
          {phase === 'streaming' && (
            <><span className="spinner" style={{ marginRight: 10 }} />Generando análisis…</>
          )}
          {phase === 'done' && '✓ Análisis completado'}
          {phase === 'error' && '✗ Error'}
        </h1>
        {phase === 'done' && (
          <div className="flex gap-2">
            <Link to="/dashboard" className="btn btn-secondary btn-sm">← Dashboard</Link>
            <Link to="/analysis/new" className="btn btn-primary btn-sm">Nuevo análisis</Link>
          </div>
        )}
      </div>

      {errorMsg && <div className="alert alert-error">{errorMsg}</div>}

      {/* Thinking steps */}
      {steps.length > 0 && (
        <>
          {phase === 'done' ? (
            <details style={{ marginBottom: 24 }}>
              <summary style={{ cursor: 'pointer', fontWeight: 500, padding: '10px 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Proceso del agente ({steps.length} pasos)
              </summary>
              <div className="steps-wrapper" style={{ marginTop: 12 }}>
                {steps.map((step, i) => (
                  <ThinkingStep key={i} step={step} isLast={false} isStreaming={false} />
                ))}
              </div>
            </details>
          ) : (
            <div className="steps-wrapper">
              {steps.map((step, i) => (
                <ThinkingStep
                  key={i}
                  step={step}
                  isLast={i === steps.length - 1}
                  isStreaming={phase === 'streaming'}
                />
              ))}
            </div>
          )}
        </>
      )}

      <div ref={stepsEndRef} />

      {/* Final analysis */}
      {finalAnalysis && (
        <>
          <div className="card mb-4" style={{ background: 'var(--primary-light)', borderColor: '#bfdbfe' }}>
            <div className="text-sm text-muted mb-1">Consulta</div>
            <p style={{ fontWeight: 500 }}>{finalAnalysis.query}</p>
          </div>
          <div className="card">
            <MarkdownRenderer content={finalAnalysis.analysis} />
          </div>
          <div className="mt-4 flex gap-2">
            <Link to={`/analysis/${finalAnalysis.analysis_id}`} className="btn btn-secondary btn-sm">
              Ver análisis guardado
            </Link>
          </div>
        </>
      )}
    </Layout>
  )
}
