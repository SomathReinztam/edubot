import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import ModelConfig from './ModelConfig'
import { streamAnalysis } from '../api'

const DEFAULT_MODELS = {
  analyst: { client: 'google', model: 'gemini-2.0-flash', temperature: 0.7, api_key: '' },
  querier: { client: 'google', model: 'gemini-2.0-flash', temperature: 0.0, api_key: '' },
  halting: { client: 'google', model: 'gemini-2.0-flash', temperature: 0.0, api_key: '' },
}

function loadSavedModels() {
  try {
    const saved = localStorage.getItem('edubot_model_config')
    return saved ? JSON.parse(saved) : DEFAULT_MODELS
  } catch {
    return DEFAULT_MODELS
  }
}

export default function AnalysisRunner({ user, onAnalysisComplete }) {
  const [phase, setPhase] = useState('form') // 'form' | 'streaming' | 'done'
  const [query, setQuery] = useState('')
  const [topN, setTopN] = useState(10)
  const [showModelConfig, setShowModelConfig] = useState(false)
  const [models, setModels] = useState(loadSavedModels)
  const [reasoningSteps, setReasoningSteps] = useState([])
  const [finalAnalysis, setFinalAnalysis] = useState('')
  const [error, setError] = useState('')
  const [currentQuery, setCurrentQuery] = useState('')

  const reasoningEndRef = useRef(null)

  useEffect(() => {
    if (phase === 'streaming' && reasoningEndRef.current) {
      reasoningEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [reasoningSteps, phase])

  const saveModels = (newModels) => {
    setModels(newModels)
    localStorage.setItem('edubot_model_config', JSON.stringify(newModels))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setCurrentQuery(query)
    setPhase('streaming')
    setReasoningSteps([])
    setFinalAnalysis('')
    setError('')

    const payload = {
      user_id: user.user_id,
      query,
      top_n: topN,
      model_analyst: models.analyst,
      model_querier: models.querier,
      model_halting: models.halting,
    }

    await streamAnalysis(
      payload,
      (step) => setReasoningSteps(prev => [...prev, step]),
      (analysis) => {
        setFinalAnalysis(analysis)
        setPhase('done')
        onAnalysisComplete?.()
      },
      (errMsg) => {
        setError(errMsg)
        setPhase('form')
      },
    )
  }

  if (phase === 'form') {
    return (
      <div className="analysis-form-container">
        <h2>Nueva Análisis</h2>
        <form onSubmit={handleSubmit} className="analysis-form">
          <div className="form-group">
            <label>Consulta</label>
            <textarea
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="¿Qué te gustaría analizar? Ej: Dame un resumen de la actividad de los últimos 30 días en los canales de proyectos..."
              rows={5}
              required
            />
          </div>

          <div className="form-group form-group-inline">
            <label>Top N resultados por consulta</label>
            <input
              type="number"
              value={topN}
              onChange={e => setTopN(Math.max(1, parseInt(e.target.value) || 1))}
              min={1}
              max={100}
              className="input-small"
            />
          </div>

          <div className="collapsible-section">
            <button
              type="button"
              className="collapsible-header"
              onClick={() => setShowModelConfig(v => !v)}
            >
              <span>⚙️ Configuración de Modelos</span>
              <span className="chevron">{showModelConfig ? '▲' : '▼'}</span>
            </button>
            {showModelConfig && (
              <div className="collapsible-body">
                <ModelConfig models={models} onChange={saveModels} />
              </div>
            )}
          </div>

          {error && <div className="error-msg">{error}</div>}

          <button type="submit" className="btn-primary btn-large">
            Generar Reporte
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="analysis-view">
      <div className="analysis-view-header">
        <div className="analysis-query-badge">
          <span className="query-label">Consulta</span>
          <span className="query-text">"{currentQuery}"</span>
        </div>
        {phase === 'streaming' && (
          <div className="streaming-pill">
            <span className="streaming-dot" />
            Analizando...
          </div>
        )}
      </div>

      <div className="reasoning-section">
        <h3 className="section-title">Razonamiento del agente</h3>
        <div className="reasoning-steps">
          {reasoningSteps.map((step, i) => (
            <div
              key={i}
              className={`reasoning-card ${step.role === 'Analista' ? 'card-analyst' : 'card-querier'}`}
            >
              <div className="reasoning-role-badge">{step.role}</div>
              <div className="reasoning-content markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {step.content || '*Procesando...*'}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {phase === 'streaming' && (
            <div className="typing-indicator">
              <span /><span /><span />
            </div>
          )}
          <div ref={reasoningEndRef} />
        </div>
      </div>

      {finalAnalysis && (
        <div className="final-analysis-section">
          <h3 className="section-title">Reporte Final</h3>
          <div className="final-analysis-card markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {finalAnalysis}
            </ReactMarkdown>
          </div>
          <button
            className="btn-secondary"
            onClick={() => { setPhase('form'); setQuery('') }}
          >
            Nueva Consulta
          </button>
        </div>
      )}
    </div>
  )
}
