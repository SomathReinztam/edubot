import { useState } from 'react'

const MODELS = {
  google: [
    'gemini-2.0-flash',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-3-flash-preview',
    'gemini-3.1-flash-lite-preview',
    'gemini-3.1-pro-preview',
  ],
  groq: [
    'llama-3.3-70b-versatile',
    'openai/gpt-oss-120b',
    'moonshotai/kimi-k2-instruct-0905',
  ],
  deepseek: ['deepseek-chat', 'deepseek-reasoner'],
}

function SingleModelConfig({ label, value, onChange }) {
  const modelList = MODELS[value.client] || []

  const handleClientChange = (e) => {
    const client = e.target.value
    onChange({ ...value, client, model: MODELS[client][0] })
  }

  return (
    <div className="single-model-config">
      <div className="model-fields">
        <div className="form-group">
          <label>Proveedor</label>
          <select value={value.client} onChange={handleClientChange}>
            <option value="google">Google</option>
            <option value="groq">Groq</option>
            <option value="deepseek">DeepSeek</option>
          </select>
        </div>
        <div className="form-group">
          <label>Modelo</label>
          <select value={value.model} onChange={e => onChange({ ...value, model: e.target.value })}>
            {modelList.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Temperatura: <strong>{value.temperature}</strong></label>
          <input
            type="range"
            min={0}
            max={2}
            step={0.1}
            value={value.temperature}
            onChange={e => onChange({ ...value, temperature: parseFloat(e.target.value) })}
          />
        </div>
        <div className="form-group">
          <label>API Key</label>
          <input
            type="password"
            value={value.api_key}
            onChange={e => onChange({ ...value, api_key: e.target.value })}
            placeholder="Ingresa tu API key"
          />
        </div>
      </div>
    </div>
  )
}

const ROLE_LABELS = { analyst: 'Analista', querier: 'Consultador', halting: 'Clasificador' }

export default function ModelConfig({ models, onChange }) {
  const [activeTab, setActiveTab] = useState('analyst')

  return (
    <div className="model-config">
      <div className="model-tabs">
        {Object.keys(ROLE_LABELS).map(key => (
          <button
            key={key}
            type="button"
            className={`model-tab ${activeTab === key ? 'active' : ''}`}
            onClick={() => setActiveTab(key)}
          >
            {ROLE_LABELS[key]}
          </button>
        ))}
      </div>
      <SingleModelConfig
        label={ROLE_LABELS[activeTab]}
        value={models[activeTab]}
        onChange={val => onChange({ ...models, [activeTab]: val })}
      />
    </div>
  )
}
