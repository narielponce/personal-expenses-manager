<template>
  <div class="home-container py-1">
    <!-- User Greeting Section -->
    <div class="user-header mb-2 mt-1 px-1">
      <h5 class="fw-bold mb-0">Hola, <span class="text-primary">{{ userName }}</span> 👋</h5>
      <p class="text-muted tiny mb-0">¿Qué registramos hoy?</p>
    </div>

    <!-- Quick Action Section (Audio & Photo) -->
    <div class="row g-2 mb-2">
      <div class="col-6 text-center">
        <button 
          class="btn btn-action audio-btn shadow-sm w-100 d-flex flex-column align-items-center justify-content-center py-3 h-100"
          @click="toggleRecording"
          :disabled="isProcessingVoice || isProcessingImage"
          :class="{ 'recording-active pulse-red': isRecording }"
        >
          <div class="icon-square mb-1 text-white">
            <i class="bi" :class="isRecording ? 'bi-stop-fill' : 'bi-mic-fill'"></i>
          </div>
          <span class="fw-bold text-white smaller">{{ isRecording ? 'Escuchando' : (isProcessingVoice ? 'Procesando' : 'Audio') }}</span>
        </button>
      </div>
      <div class="col-6 text-center">
        <button 
          class="btn btn-action photo-btn shadow-sm w-100 d-flex flex-column align-items-center justify-content-center py-3 h-100"
          @click="triggerPhotoInput"
          :disabled="isProcessingVoice || isProcessingImage"
        >
          <div class="icon-square mb-1 text-white">
            <i class="bi" :class="isProcessingImage ? 'bi-hourglass-split' : 'bi-camera-fill'"></i>
          </div>
          <span class="fw-bold text-white smaller">{{ isProcessingImage ? 'Procesando' : 'Foto' }}</span>
        </button>
        <!-- Input oculto para cámara/archivos -->
        <input 
          type="file" 
          ref="photoInput" 
          class="d-none" 
          accept="image/*" 
          capture="environment"
          @change="handlePhotoCapture"
        />
      </div>
    </div>

    <!-- Inbox Preview Section -->
    <div class="inbox-preview card border-0 shadow-sm rounded-4 overflow-hidden mb-2">
      <!-- Drag Handle -->
      <div class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>
      
      <div class="card-header bg-white border-0 pt-0 px-3 d-flex justify-content-between align-items-center">
        <h6 class="mb-0 fw-bold smaller">Inbox de Gastos</h6>
        <span class="badge rounded-pill bg-danger-subtle text-danger px-2 py-1" style="font-size: 0.6rem;">
          {{ inboxExpenses.length }} pendientes
        </span>
      </div>
      <div class="card-body p-2">
        <div v-if="loading" class="text-center py-2">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
        </div>
        <div v-else-if="inboxExpenses.length > 0">
          <div v-for="expense in inboxExpenses.slice(0, 3)" :key="expense.id" class="inbox-item d-flex align-items-center p-2 mb-1 rounded-3">
            <div class="flex-shrink-0 me-2">
              <div class="inbox-icon bg-light rounded-circle d-flex align-items-center justify-content-center">
                <i class="bi bi-question-circle text-muted tiny"></i>
              </div>
            </div>
            <div class="flex-grow-1 min-width-0">
              <div class="d-flex justify-content-between align-items-center">
                <p class="mb-0 fw-bold text-dark text-truncate tiny">{{ expense.description || 'Sin descripción' }}</p>
                <p class="mb-0 fw-bold text-dark tiny">{{ formatCurrency(expense.amount) }}</p>
              </div>
              <p class="mb-0 text-muted tiny-sub">{{ formatDate(expense.date) }}</p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-3">
          <i class="bi bi-check-circle text-success fs-4 opacity-25"></i>
          <p class="text-muted tiny mt-1">¡Todo al día!</p>
        </div>
      </div>
      
      <div class="card-footer bg-white border-top p-2 text-center">
        <router-link to="/inbox" class="btn btn-primary btn-sm w-100 rounded-pill fw-bold py-2 shadow-sm">
          Revisar Inbox
        </router-link>
        
        <div class="mt-2">
          <router-link to="/expenses/new" class="text-decoration-none text-muted tiny">
            <i class="bi bi-plus-circle me-1"></i> Registro Manual
          </router-link>
        </div>
      </div>
    </div>

    <!-- Cuentas y Saldos Widget -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-2">
      <div class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>
      <div class="card-body p-3 pt-1">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="tiny text-muted fw-bold text-uppercase">Mis Cuentas</span>
          <router-link to="/accounts" class="text-decoration-none tiny fw-bold text-primary">
            Gestionar <i class="bi bi-chevron-right" style="font-size: 0.65rem;"></i>
          </router-link>
        </div>

        <div class="d-flex justify-content-between align-items-baseline mb-2">
          <div>
            <span class="tiny text-muted d-block text-uppercase" style="font-size: 0.6rem;">Disponible Líquido</span>
            <h4 class="fw-bold mb-0" :class="totalLiquidity < 0 ? 'text-danger' : 'text-dark'">
              {{ formatCurrency(totalLiquidity) }}
            </h4>
          </div>
          <div v-if="hasOverdrawnAccount" class="text-end">
            <span class="badge bg-danger text-white tiny px-2 py-1">
              <i class="bi bi-exclamation-circle-fill me-1"></i>En Descubierto
            </span>
          </div>
          <div v-else-if="totalCreditDebt > 0" class="text-end">
            <span class="tiny text-muted d-block text-uppercase" style="font-size: 0.6rem;">Deuda Tarjetas</span>
            <span class="smaller fw-bold text-danger">{{ formatCurrency(totalCreditDebt) }}</span>
          </div>
        </div>

        <!-- Scroll horizontal de cuentas -->
        <div v-if="accountsWithBalances.length > 0" class="d-flex gap-2 overflow-auto pb-1" style="scrollbar-width: thin;">
          <div 
            v-for="acc in accountsWithBalances" 
            :key="acc.id"
            class="p-2 rounded-3 border bg-light flex-shrink-0"
            style="min-width: 130px; max-width: 160px;"
          >
            <div class="d-flex justify-content-between align-items-center mb-1">
              <span class="tiny text-truncate fw-bold text-dark d-block" :title="acc.name" style="max-width: 100px;">
                {{ acc.name }}
              </span>
              <i class="bi" :class="acc.is_credit_card ? 'bi-credit-card tiny text-primary' : 'bi-bank tiny text-muted'"></i>
            </div>
            <div 
              class="smaller fw-bold text-truncate"
              :class="acc.is_overdrawn ? 'text-danger' : 'text-dark'"
            >
              {{ formatCurrency(acc.current_balance) }}
            </div>
            <span v-if="acc.is_overdrawn && !acc.is_credit_card" class="badge bg-danger text-white p-0 px-1 mt-1" style="font-size: 0.55rem;">
              Descubierto
            </span>
            <span v-else-if="acc.is_credit_card" class="tiny text-muted d-block" style="font-size: 0.58rem;">
              Tarjeta
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Summary -->
    <div class="card border-0 bg-primary text-white rounded-4 shadow-sm p-3 mb-2">
      <div class="d-flex justify-content-between align-items-center">
        <span class="tiny opacity-75 fw-bold text-uppercase">Gasto del Mes</span>
        <i class="bi bi-wallet2 opacity-50 tiny"></i>
      </div>
      <h4 class="fw-bold mb-0 mt-1">{{ formatCurrency(totalSpent) }}</h4>
    </div>

    <!-- Proyección de Cierre de Mes (Run-rate) -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-2">
      <div class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>
      <div class="card-body p-3 pt-1">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <span class="tiny text-muted fw-bold text-uppercase">Proyección Cierre de Mes</span>
          <span class="badge rounded-pill px-2 py-1" :class="projectionBadgeClass" style="font-size: 0.65rem;">
            {{ projectionBadgeText }}
          </span>
        </div>
        <div class="d-flex justify-content-between align-items-baseline mb-2">
          <h4 class="fw-bold mb-0 text-dark">{{ formatCurrency(projectedMonthEnd) }}</h4>
          <span class="tiny text-muted">Ritmo: <strong>{{ formatCurrency(dailyVariableRate) }}/día</strong></span>
        </div>

        <!-- Barra de progreso visual -->
        <div class="mb-2">
          <div class="d-flex justify-content-between tiny text-muted mb-1">
            <span>Día {{ daysElapsed }} de {{ daysInMonth }} ({{ timeProgressPct }}% mes)</span>
            <span>Gastado: {{ formatCurrency(totalSpentSoFar) }}</span>
          </div>
          <div class="progress" style="height: 7px; border-radius: 4px; background-color: #e9ecef;">
            <div 
              class="progress-bar rounded-pill" 
              role="progressbar" 
              :style="{ width: progressPercentage + '%' }"
              :class="progressBarClass"
            ></div>
          </div>
        </div>

        <div class="row g-2 text-center pt-1 border-top mt-2">
          <div class="col-6 border-end">
            <span class="tiny text-muted d-block text-uppercase">Gastos Fijos</span>
            <strong class="smaller text-dark">{{ formatCurrency(fixedSpent) }}</strong>
          </div>
          <div class="col-6">
            <span class="tiny text-muted d-block text-uppercase">Gastos Variables</span>
            <strong class="smaller text-dark">{{ formatCurrency(variableSpent) }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Copiloto Financiero IA -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-3">
      <div class="d-flex justify-content-center pt-2 pb-1">
        <div class="drag-handle"></div>
      </div>
      <div class="card-header bg-white border-0 pt-0 px-3 d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-2">
          <i class="bi bi-stars text-primary fs-5"></i>
          <h6 class="mb-0 fw-bold smaller text-dark">Copiloto Financiero IA</h6>
        </div>
        <button 
          class="btn btn-outline-primary btn-sm rounded-pill tiny px-2 py-1 d-flex align-items-center gap-1"
          @click="generateDiagnosis(true)"
          :disabled="loadingAdvisor"
        >
          <span v-if="loadingAdvisor" class="spinner-border spinner-border-sm" role="status"></span>
          <i v-else class="bi bi-arrow-clockwise"></i>
          <span>{{ advisorData ? 'Actualizar' : 'Analizar' }}</span>
        </button>
      </div>

      <div class="card-body p-3 pt-1">
        <div v-if="loadingAdvisor" class="text-center py-4">
          <div class="spinner-grow text-primary mb-2" role="status" style="width: 2rem; height: 2rem;"></div>
          <p class="text-muted tiny mb-0">Gemini está analizando tu proyección y gastos...</p>
        </div>

        <div v-else-if="advisorData">
          <!-- Diagnóstico General -->
          <div class="p-3 rounded-3 mb-2" :class="advisorStatusBgClass">
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge rounded-pill" :class="advisorBadgeClass" style="font-size: 0.65rem;">
                {{ (advisorData.status_color || 'estado').toUpperCase() }}
              </span>
              <span class="tiny fw-bold text-dark">Diagnóstico del Asesor</span>
            </div>
            <p class="mb-0 tiny text-dark">{{ advisorData.diagnosis }}</p>
          </div>

          <!-- Alertas Críticas / Hormiga -->
          <div v-if="advisorData.alerts && advisorData.alerts.length" class="mb-2">
            <span class="tiny text-muted fw-bold text-uppercase d-block mb-1">Alertas Detectadas</span>
            <div v-for="(alertItem, idx) in advisorData.alerts" :key="idx" class="d-flex align-items-start gap-2 p-2 bg-light rounded-3 mb-1">
              <i class="bi bi-exclamation-triangle-fill text-warning tiny mt-1"></i>
              <span class="tiny text-dark">{{ alertItem }}</span>
            </div>
          </div>

          <!-- 3 Recomendaciones Accionables -->
          <div v-if="advisorData.recommendations && advisorData.recommendations.length" class="mb-2">
            <span class="tiny text-muted fw-bold text-uppercase d-block mb-1">Recomendaciones Accionables</span>
            <div v-for="(rec, idx) in advisorData.recommendations" :key="idx" class="d-flex align-items-start gap-2 p-2 bg-light rounded-3 mb-1">
              <i class="bi bi-check-circle-fill text-success tiny mt-1"></i>
              <span class="tiny text-dark">{{ rec }}</span>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-3 bg-light rounded-4">
          <i class="bi bi-robot text-primary fs-2 opacity-50"></i>
          <p class="text-muted tiny mt-1 mb-2">Obtén un diagnóstico predictivo y recomendaciones inteligentes con Gemini.</p>
          <button 
            class="btn btn-primary btn-sm rounded-pill fw-bold px-3 py-1 shadow-sm tiny"
            @click="generateDiagnosis(false)"
          >
            <i class="bi bi-stars me-1"></i> Generar Análisis
          </button>
        </div>

        <!-- Botón Simulador de Compras -->
        <div class="mt-3 pt-2 border-top text-center">
          <button 
            type="button" 
            class="btn btn-outline-secondary btn-sm w-100 rounded-pill tiny fw-bold py-2 shadow-sm"
            data-bs-toggle="modal" 
            data-bs-target="#simulationModal"
          >
            <i class="bi bi-calculator me-1 text-primary"></i> Simular Compra en Cuotas con IA
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Simulador de Compra en Cuotas -->
    <div class="modal fade" id="simulationModal" tabindex="-1" aria-labelledby="simulationModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4 border-0 shadow">
          <div class="d-flex justify-content-center pt-2 pb-1">
            <div class="drag-handle"></div>
          </div>
          <div class="modal-header border-0 pt-0 pb-1 px-3">
            <h6 class="modal-title fw-bold smaller text-dark" id="simulationModalLabel">
              <i class="bi bi-calculator text-primary me-1"></i> Simular Compra en Cuotas
            </h6>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-3">
            <p class="text-muted tiny mb-3">Descubre con IA si una compra planeada es viable y cómo afectará tus próximos meses.</p>
            <form @submit.prevent="runPurchaseSimulation">
              <div class="mb-2">
                <label for="simDesc" class="form-label tiny text-muted fw-bold text-uppercase mb-1">Artículo / Gasto:</label>
                <input type="text" class="form-control form-control-sm rounded-3 bg-light border-0" id="simDesc" v-model="simForm.description" placeholder="Ej: Zapatillas deportivas" required />
              </div>
              <div class="row g-2 mb-2">
                <div class="col-6">
                  <label for="simAmount" class="form-label tiny text-muted fw-bold text-uppercase mb-1">Monto Total ($):</label>
                  <input type="number" step="0.01" class="form-control form-control-sm rounded-3 bg-light border-0" id="simAmount" v-model="simForm.amount" placeholder="0.00" required />
                </div>
                <div class="col-6">
                  <label for="simInstallments" class="form-label tiny text-muted fw-bold text-uppercase mb-1">Cuotas:</label>
                  <select class="form-select form-select-sm rounded-3 bg-light border-0" id="simInstallments" v-model="simForm.installments">
                    <option :value="1">1 pago</option>
                    <option :value="2">2 cuotas</option>
                    <option :value="3">3 cuotas</option>
                    <option :value="6">6 cuotas</option>
                    <option :value="12">12 cuotas</option>
                    <option :value="18">18 cuotas</option>
                    <option :value="24">24 cuotas</option>
                  </select>
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 rounded-pill fw-bold py-2 shadow-sm tiny mt-2" :disabled="loadingSimulation">
                <span v-if="loadingSimulation" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-stars me-1"></i> Evaluar Viabilidad con IA
              </button>
            </form>

            <!-- Resultado de Simulación -->
            <div v-if="simulationResult" class="mt-3 p-3 rounded-4 border" :class="simResultBorderClass">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge rounded-pill px-2 py-1" :class="simResultBadgeClass" style="font-size: 0.7rem;">
                  {{ simulationResult.verdict }} - {{ simulationResult.verdict_title }}
                </span>
                <span class="smaller fw-bold text-dark">{{ formatCurrency(simulationResult.monthly_installment) }} / mes</span>
              </div>
              <p class="tiny text-dark mb-2">{{ simulationResult.impact_summary }}</p>
              <div class="p-2 bg-light rounded-3 d-flex align-items-start gap-2">
                <i class="bi bi-lightbulb-fill text-warning tiny mt-1"></i>
                <span class="tiny text-muted"><strong>Consejo:</strong> {{ simulationResult.actionable_tip }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <Transition name="fade">
      <div v-if="showSuccessToast" class="success-toast shadow-sm rounded-pill py-2 px-4 bg-success text-white d-flex align-items-center gap-2">
        <i class="bi bi-check-circle-fill"></i>
        <span class="fw-bold tiny">{{ toastMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useExpenseStore } from '../stores/expense';
import { useAuthStore } from '../stores/auth';
import { useAnalyticsStore } from '../stores/analytics';
import { useAccountStore } from '../stores/account';
import apiClient from '../api';
import { useRouter } from 'vue-router';

const expenseStore = useExpenseStore();
const authStore = useAuthStore();
const analyticsStore = useAnalyticsStore();
const accountStore = useAccountStore();
const router = useRouter();

const expenses = computed(() => expenseStore.expenses);
const loading = computed(() => expenseStore.loading);
const summary = computed(() => analyticsStore.summary);
const advisorData = computed(() => analyticsStore.advisor);
const loadingAdvisor = computed(() => analyticsStore.loadingAdvisor);
const loadingSimulation = computed(() => analyticsStore.loadingSimulation);
const simulationResult = computed(() => analyticsStore.simulationResult);

const accountsWithBalances = computed(() => accountStore.accountsWithBalances);
const totalLiquidity = computed(() => accountStore.totalLiquidity);
const totalCreditDebt = computed(() => accountStore.totalCreditDebt);
const hasOverdrawnAccount = computed(() => accountsWithBalances.value.some(a => a.is_overdrawn && !a.is_credit_card));

const userName = computed(() => {
  if (authStore.user && authStore.user.email) {
    return authStore.user.email.split('@')[0];
  }
  return 'Usuario';
});

// Proyección y Métricas
const projection = computed(() => summary.value?.projection || {});
const projectedMonthEnd = computed(() => projection.value.projected_month_end || 0);
const dailyVariableRate = computed(() => projection.value.daily_variable_rate || 0);
const daysElapsed = computed(() => projection.value.days_elapsed || 0);
const daysInMonth = computed(() => projection.value.days_in_month || 30);
const timeProgressPct = computed(() => projection.value.time_progress_pct || 0);
const totalSpentSoFar = computed(() => projection.value.total_spent_so_far || 0);
const fixedSpent = computed(() => projection.value.fixed_recurring_spent || 0);
const variableSpent = computed(() => projection.value.variable_spent_so_far || 0);

const progressPercentage = computed(() => {
  if (!projectedMonthEnd.value || projectedMonthEnd.value <= 0) return 0;
  return Math.min(100, Math.round((totalSpentSoFar.value / projectedMonthEnd.value) * 100));
});

const projectionBadgeClass = computed(() => {
  const diff = progressPercentage.value - timeProgressPct.value;
  if (diff > 15) return 'bg-danger-subtle text-danger';
  if (diff > 5) return 'bg-warning-subtle text-warning-emphasis';
  return 'bg-success-subtle text-success';
});

const projectionBadgeText = computed(() => {
  const diff = progressPercentage.value - timeProgressPct.value;
  if (diff > 15) return 'Ritmo Acelerado';
  if (diff > 5) return 'En Alerta';
  return 'Ritmo Saludable';
});

const progressBarClass = computed(() => {
  const diff = progressPercentage.value - timeProgressPct.value;
  if (diff > 15) return 'bg-danger';
  if (diff > 5) return 'bg-warning';
  return 'bg-success';
});

const advisorStatusBgClass = computed(() => {
  const color = (advisorData.value?.status_color || '').toLowerCase();
  if (color === 'rojo') return 'bg-danger-subtle border-start border-4 border-danger';
  if (color === 'amarillo') return 'bg-warning-subtle border-start border-4 border-warning';
  return 'bg-success-subtle border-start border-4 border-success';
});

const advisorBadgeClass = computed(() => {
  const color = (advisorData.value?.status_color || '').toLowerCase();
  if (color === 'rojo') return 'bg-danger text-white';
  if (color === 'amarillo') return 'bg-warning text-dark';
  return 'bg-success text-white';
});

const simResultBadgeClass = computed(() => {
  const v = (simulationResult.value?.verdict || '').toLowerCase();
  if (v.includes('rojo')) return 'bg-danger text-white';
  if (v.includes('amarillo')) return 'bg-warning text-dark';
  return 'bg-success text-white';
});

const simResultBorderClass = computed(() => {
  const v = (simulationResult.value?.verdict || '').toLowerCase();
  if (v.includes('rojo')) return 'border-danger bg-danger-subtle bg-opacity-25';
  if (v.includes('amarillo')) return 'border-warning bg-warning-subtle bg-opacity-25';
  return 'border-success bg-success-subtle bg-opacity-25';
});

// Simulador de Compras
const simForm = ref({
  description: '',
  amount: '',
  installments: 3
});

const runPurchaseSimulation = async () => {
  if (!simForm.value.amount || Number(simForm.value.amount) <= 0) return;
  try {
    await analyticsStore.simulatePurchase({
      amount: Number(simForm.value.amount),
      installments: Number(simForm.value.installments),
      description: simForm.value.description || 'Compra planeada'
    });
  } catch (err) {
    console.error('Error al simular:', err);
  }
};

const generateDiagnosis = async (force = false) => {
  await analyticsStore.fetchAdvisor(force);
};

// Estado de grabación de voz e imagen
const isRecording = ref(false);
const isProcessingVoice = ref(false);
const isProcessingImage = ref(false);
const showSuccessToast = ref(false);
const toastMessage = ref('');
const photoInput = ref(null);
let recognition = null;

const inboxExpenses = computed(() => {
  return expenses.value.filter(exp => exp.status === 'pending');
});

const totalSpent = computed(() => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    return expenses.value
        .filter(exp => {
            const expDate = new Date(exp.date);
            return expDate.getMonth() === currentMonth && expDate.getFullYear() === currentYear && exp.movement_type === 'expense' && exp.status === 'completed';
        })
        .reduce((sum, exp) => sum + exp.amount, 0);
});

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0.00';
  const formattedValue = new Intl.NumberFormat('es-ES', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2, 
    useGrouping: true 
  }).format(Number(value));
  return '$' + formattedValue;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const pureDate = dateStr.includes('T') ? dateStr.split('T')[0] : dateStr;
  const [year, month, day] = pureDate.split('-');
  return new Date(year, month - 1, day).toLocaleDateString();
};

// --- Lógica de Voz ---
const toggleRecording = () => {
  if (isRecording.value) {
    if (recognition) recognition.stop();
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Lo siento, tu navegador no soporta reconocimiento de voz.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'es-ES';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isRecording.value = true;
  };

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    processVoiceText(text);
  };

  recognition.onerror = (event) => {
    console.error("Error en reconocimiento:", event.error);
    isRecording.value = false;
  };

  recognition.onend = () => {
    isRecording.value = false;
  };

  recognition.start();
};

const processVoiceText = async (text) => {
  isProcessingVoice.value = true;
  try {
    await expenseStore.processVoiceAndSave(text);
    await expenseStore.fetchExpenses(0, 50);
    await analyticsStore.fetchSummary();
    
    toastMessage.value = "Gasto enviado al Inbox";
    showSuccessToast.value = true;
    setTimeout(() => {
      showSuccessToast.value = false;
    }, 2000);
  } catch (err) {
    console.error("Error al procesar voz con Gemini:", err);
    alert("Hubo un error al procesar tu voz con la IA. Por favor, inténtalo de nuevo.");
  } finally {
    isProcessingVoice.value = false;
  }
};

// --- Lógica de Imagen ---
const triggerPhotoInput = () => {
  if (photoInput.value) {
    photoInput.value.click();
  }
};

const handlePhotoCapture = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isProcessingImage.value = true;
  try {
    await expenseStore.processImageAndSave(file);
    await expenseStore.fetchExpenses(0, 50);
    await analyticsStore.fetchSummary();
    
    toastMessage.value = "Ticket enviado al Inbox";
    showSuccessToast.value = true;
    setTimeout(() => {
      showSuccessToast.value = false;
    }, 2000);
  } catch (err) {
    console.error("Error al procesar imagen con Gemini:", err);
    alert("No pudimos procesar la imagen del ticket. Asegúrate de que sea clara.");
  } finally {
    isProcessingImage.value = false;
    event.target.value = '';
  }
};

onMounted(async () => {
  await expenseStore.fetchExpenses(0, 50);
  await analyticsStore.fetchSummary();
  await accountStore.fetchAccountsWithBalances();
});
</script>

<style scoped>
.btn-action {
  border: none;
  border-radius: 1.5rem;
  transition: all 0.2s ease;
}

.btn-action:active {
  transform: scale(0.95);
  opacity: 0.9;
}

.audio-btn {
  background-color: #0d6efd;
}

.photo-btn {
  background-color: #198754;
}

.icon-square {
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin-left: auto;
  margin-right: auto;
}

.pulse-red {
  animation: pulse-recording 1.5s infinite;
  background-color: #dc3545 !important;
}

@keyframes pulse-recording {
  0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
  70% { box-shadow: 0 0 0 15px rgba(220, 53, 69, 0); }
  100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
}

.drag-handle {
  width: 36px;
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  position: relative;
}

.drag-handle::before, .drag-handle::after {
  content: "";
  position: absolute;
  width: 4px;
  height: 4px;
  background-color: #e9ecef;
  border-radius: 50%;
  top: 0;
}
.drag-handle::before { left: -8px; }
.drag-handle::after { right: -8px; }

.inbox-item {
  transition: background-color 0.2s;
}

.inbox-icon {
  width: 32px;
  height: 32px;
}

.home-container {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.smaller {
  font-size: 0.75rem;
}

.tiny {
  font-size: 0.7rem;
}

.tiny-sub {
  font-size: 0.6rem;
}

@media (min-width: 768px) {
  .smaller {
    font-size: 0.95rem;
  }
  .tiny {
    font-size: 0.85rem;
  }
  .tiny-sub {
    font-size: 0.75rem;
  }
  .inbox-item p.tiny {
    font-size: 0.95rem !important;
  }
  .inbox-item p.tiny-sub {
    font-size: 0.8rem !important;
  }
  .inbox-icon {
    width: 38px;
    height: 38px;
  }
  .inbox-icon i {
    font-size: 1rem !important;
  }
  .user-header h5 {
    font-size: 1.35rem;
  }
  .user-header p {
    font-size: 0.85rem !important;
  }
}

.min-width-0 {
  min-width: 0;
}

.success-toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
