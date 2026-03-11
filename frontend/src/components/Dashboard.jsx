import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import AnalysisRunner from './AnalysisRunner'
import { getUserAnalyses, getAnalysis } from '../api'

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit', month: 'short', year: 'numeric'
    })
  } catch {
    return dateStr
  }
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleString('es-ES', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

export default function Dashboard({ user, onLogout }) {
  const [analyses, setAnalyses] = useState([])
  const [view, setView] = useState('new') // 'new' | 'detail'
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  const fetchHistory = async () => {
    try {
      const data = await getUserAnalyses(user.user_id)
      setAnalyses(data)
    } catch {
      // silently ignore
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const handleSelectAnalysis = async (analysisId) => {
    setLoadingDetail(true)
    try {
      const data = await getAnalysis(analysisId)
      setSelectedAnalysis(data)
      setView('detail')
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingDetail(false)
    }
  }

  const handleNewAnalysis = () => {
    setView('new')
    setSelectedAnalysis(null)
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-brand">🤖 EduBot</div>
        <div className="header-user">
          <span className="header-username">{user.name}</span>
          <button onClick={onLogout} className="btn-ghost">Cerrar sesión</button>
        </div>
      </header>

      <div className="dashboard-body">
        <aside className="sidebar">
          <button className="btn-primary sidebar-new-btn" onClick={handleNewAnalysis}>
            + Nueva Análisis
          </button>

          <div className="sidebar-section-title">Historial</div>

          <ul className="analysis-list">
            {analyses.length === 0 && (
              <li className="analysis-list-empty">Sin análisis aún</li>
            )}
            {analyses.map(a => (
              <li
                key={a.analysis_id}
                className={`analysis-list-item ${selectedAnalysis?.analysis_id === a.analysis_id && view === 'detail' ? 'active' : ''}`}
                onClick={() => handleSelectAnalysis(a.analysis_id)}
              >
                <div className="analysis-list-query">{a.query}</div>
                <div className="analysis-list-date">{formatDate(a.created_at)}</div>
              </li>
            ))}
          </ul>
        </aside>

        <main className="main-content">
          {view === 'new' && (
            <AnalysisRunner
              user={user}
              onAnalysisComplete={fetchHistory}
            />
          )}

          {view === 'detail' && (
            <div className="analysis-detail">
              {loadingDetail ? (
                <div className="loading-state">Cargando análisis...</div>
              ) : selectedAnalysis ? (
                <>
                  <div className="analysis-detail-header">
                    <h2>{selectedAnalysis.query}</h2>
                    <span className="analysis-detail-date">
                      {formatDateTime(selectedAnalysis.created_at)}
                    </span>
                  </div>
                  <div className="final-analysis-card markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {selectedAnalysis.analysis}
                    </ReactMarkdown>
                  </div>
                </>
              ) : null}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
