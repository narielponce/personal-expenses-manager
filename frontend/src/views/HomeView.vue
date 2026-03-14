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
      <!-- Drag Handle (The 3 dots) -->
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

    <!-- Monthly Summary -->
    <div class="card border-0 bg-primary text-white rounded-4 shadow-sm p-3">
      <div class="d-flex justify-content-between align-items-center">
        <span class="tiny opacity-75 fw-bold text-uppercase">Gasto del Mes</span>
        <i class="bi bi-info-circle opacity-50 tiny"></i>
      </div>
      <h4 class="fw-bold mb-0 mt-1">{{ formatCurrency(totalSpent) }}</h4>
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
import apiClient from '../api';
import { useRouter } from 'vue-router';

const expenseStore = useExpenseStore();
const authStore = useAuthStore();
const router = useRouter();
const expenses = computed(() => expenseStore.expenses);
const loading = computed(() => expenseStore.loading);

const userName = computed(() => {
  if (authStore.user && authStore.user.email) {
    return authStore.user.email.split('@')[0];
  }
  return 'Usuario';
});

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
    console.log("Texto detectado:", text);
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
    // Refrescamos para ver el nuevo gasto en el Inbox del Home
    await expenseStore.fetchExpenses(0, 50);
    
    // Mostrar Toast en lugar de Alert
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
    // Refrescamos la lista para ver el nuevo gasto en el Inbox
    await expenseStore.fetchExpenses(0, 50);
    
    // Mostrar Toast en lugar de Alert
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
    // Limpiar el input para permitir subir la misma foto si es necesario
    event.target.value = '';
  }
};

onMounted(async () => {
  // Cargamos los últimos 50 movimientos sin filtrar para tener confirmados y pendientes
  await expenseStore.fetchExpenses(0, 50);
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

/* Three dots style if preferred over a bar, but a bar is more common as handle */
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

.smaller {
  font-size: 0.75rem;
}

.tiny {
  font-size: 0.7rem;
}

.tiny-sub {
  font-size: 0.6rem;
}

.min-width-0 {
  min-width: 0;
}

/* Estilos para el Toast */
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
