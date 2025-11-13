<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
              <span class="text-white font-bold text-xl">AI</span>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">AI Background Remover</h1>
              <p class="text-sm text-gray-600">Powered by RMBG Models</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <!-- Portfolio logo -->
            <img :src="portfolioLogo" alt="Portfolio Logo" class="w-10 h-10 rounded-full object-cover" />
            <span class="text-sm text-gray-600">Portfolio Project</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      <!-- Upload Section -->
      <div v-if="!uploadedImage" class="card max-w-2xl mx-auto">
        <h2 class="text-xl font-semibold mb-4 text-center">Upload an Image</h2>
        
        <div
          @drop.prevent="handleDrop"
          @dragover.prevent
          @dragenter.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          :class="['border-2 border-dashed rounded-lg p-12 text-center transition-colors', 
                   isDragging ? 'border-primary bg-blue-50' : 'border-gray-300']"
        >
          <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="text-lg mb-2">Drag & drop your image here</p>
          <p class="text-sm text-gray-500 mb-4">or</p>
          <label class="btn-primary cursor-pointer inline-block">
            Browse Files
            <input type="file" class="hidden" accept="image/*" @change="handleFileSelect" />
          </label>
          <p class="text-xs text-gray-400 mt-4">Supports: JPG, PNG, WEBP</p>
        </div>

        <!-- Rate Limit Info -->
        <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-sm text-yellow-800">
            <strong>Note:</strong> Limited to 5 requests per hour per IP address.
          </p>
        </div>
      </div>

      <!-- Processing/Results Section -->
      <div v-else>
        <div class="mb-6 flex justify-between items-center">
          <button @click="reset" class="btn-secondary">
            ← Upload New Image
          </button>
        </div>

        <!-- Two-Column Layout: Original | Background Removed -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Left Column: Original Image -->
          <div class="card">
            <h3 class="text-lg font-semibold mb-4">Original</h3>
            <div class="checker-pattern rounded-lg p-4">
              <img :src="uploadedImage" alt="Original" class="w-full h-auto mx-auto" />
            </div>
          </div>

          <!-- Right Column: Background Removed -->
          <div class="card">
            <h3 class="text-lg font-semibold mb-4">Background Removed</h3>
            
            <!-- Model Buttons (shown when no results) -->
            <div v-if="selectedModels.length === 0" class="space-y-4">
              <div class="checker-pattern rounded-lg p-12 mb-4 flex items-center justify-center min-h-64">
                <div class="text-center text-gray-400">
                  <p class="text-sm mb-4">Select a model to process</p>
                </div>
              </div>
              
              <div class="grid grid-cols-1 gap-3">
                <button
                  v-for="model in models"
                  :key="model"
                  @click="processWithModel(model)"
                  :disabled="processing"
                  :class="['p-3 border-2 rounded-lg transition-all font-medium', 
                           processing ? 'opacity-50 cursor-not-allowed bg-gray-50 border-gray-200' : 'border-primary bg-blue-50 hover:bg-blue-100 cursor-pointer']"
                >
                  <span>{{ model.toUpperCase() }}</span>
                  <span v-if="processing && currentModel === model" class="ml-2 text-sm">Processing...</span>
                </button>
              </div>
            </div>

            <!-- Results Display -->
            <div v-else>
              <div v-for="model in selectedModels" :key="model" class="space-y-4">
                <div v-if="results[model]">
                  <div class="checker-pattern rounded-lg p-4 mb-4">
                    <img :src="results[model].image" alt="Result" class="w-full h-auto mx-auto" />
                  </div>
                  
                  <!-- Metadata -->
                  <div class="text-sm text-gray-600 mb-4 p-3 bg-gray-50 rounded">
                    <p><strong>Model:</strong> {{ model.toUpperCase() }}</p>
                    <p><strong>Device:</strong> {{ results[model].metadata.device_used }}</p>
                    <p><strong>Size:</strong> {{ results[model].metadata.processed_size.join(' x ') }}px</p>
                  </div>

                  <!-- Download Button -->
                  <button @click="downloadImage(results[model].image, model)" class="btn-primary w-full">
                    Download {{ model.toUpperCase() }}
                  </button>
                </div>
                <div v-else class="checker-pattern rounded-lg p-12 flex items-center justify-center min-h-48">
                  <div class="text-center text-gray-400">
                    <p class="text-sm">Processing with {{ model.toUpperCase() }}...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </main>

    <!-- Footer with Citations -->
    <footer class="bg-white border-t mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-sm text-gray-600">
          <p class="font-semibold mb-2">Model Attribution</p>
          <p class="mb-4">This tool uses RMBG models from Hugging Face</p>
          <details class="max-w-2xl mx-auto text-left">
            <summary class="cursor-pointer font-medium text-primary hover:text-blue-600 mb-2">Show Citation</summary>
            <div class="bg-gray-50 p-4 rounded mt-2 border border-gray-200">
              <div class="mb-4">
                <p class="font-semibold text-gray-900">{{ citationData.title }}</p>
              </div>
              <div class="space-y-2 text-sm text-gray-700">
                <div>
                  <span class="font-medium text-gray-800">Authors:</span>
                  <p>{{ citationData.authors.join(', ') }}</p>
                </div>
                <div>
                  <span class="font-medium text-gray-800">Journal:</span>
                  <p>{{ citationData.journal }}, {{ citationData.year }}</p>
                </div>
                <div>
                  <span class="font-medium text-gray-800">Source:</span>
                  <p><a href="https://huggingface.co/briaai/RMBG-2.0" target="_blank" class="text-primary hover:underline">Hugging Face: {{ citationData.huggingface }}</a></p>
                </div>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-200">
                <p class="font-medium text-gray-800 mb-2">BibTeX:</p>
                <pre class="bg-gray-100 p-2 rounded text-xs overflow-x-auto">{{ citationData.bibtex }}</pre>
              </div>
            </div>
          </details>
          <p class="mt-6 text-xs text-gray-400">
            © 2025 Portfolio Project | Developed by Lluís Suñol
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiService from './services/api'
// @ts-ignore - import image asset from parent directory
import portfolioLogo from '../../assets/img/ls-brain-transparent.png'

const models = ['rmbg-1.4', 'rmbg-2.0']
const selectedModels = ref<string[]>([])
const uploadedImage = ref<string | null>(null)
const results = ref<Record<string, any>>({})
const processing = ref(false)
const currentModel = ref<string | null>(null)
const error = ref<string | null>(null)
const isDragging = ref(false)

const citationData = {
  title: 'Bilateral Reference for High-Resolution Dichotomous Image Segmentation',
  authors: ['Zheng, Peng', 'Gao, Dehong', 'Fan, Deng-Ping', 'Liu, Li', 'Laaksonen, Jorma', 'Ouyang, Wanli', 'Sebe, Nicu'],
  journal: 'CAAI Artificial Intelligence Research',
  year: 2024,
  huggingface: 'briaai/RMBG-2.0',
  bibtex: `@article{BiRefNet,
  title={Bilateral Reference for High-Resolution Dichotomous Image Segmentation},
  author={Zheng, Peng and Gao, Dehong and Fan, Deng-Ping and Liu, Li and Laaksonen, Jorma and Ouyang, Wanli and Sebe, Nicu},
  journal={CAAI Artificial Intelligence Research},
  year={2024}
}`
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    loadImage(files[0])
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    loadImage(files[0])
  }
}

function loadImage(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  
  // Store file for processing
  ;(window as any).__uploadedFile = file
}

async function processWithModel(model: string) {
  if (processing.value) return
  
  error.value = null
  processing.value = true
  currentModel.value = model

  try {
    const file = (window as any).__uploadedFile
    if (!file) {
      throw new Error('No file uploaded')
    }

    const response = await apiService.removeBackground(file, model, false)
    
    results.value[model] = {
      image: `data:image/png;base64,${response.result_image}`,
      metadata: response.metadata
    }

    if (!selectedModels.value.includes(model)) {
      selectedModels.value.push(model)
    }
  } catch (err: any) {
    console.error(err)
    if (err.response?.status === 429) {
      error.value = 'Rate limit exceeded. Please wait before trying again.'
    } else {
      error.value = err.response?.data?.detail || 'Error processing image'
    }
  } finally {
    processing.value = false
    currentModel.value = null
  }
}

function downloadImage(dataUrl: string, modelName: string) {
  const link = document.createElement('a')
  link.href = dataUrl
  link.download = `background-removed-${modelName}.png`
  link.click()
}

function reset() {
  uploadedImage.value = null
  results.value = {}
  selectedModels.value = []
  error.value = null
  delete (window as any).__uploadedFile
}
</script>
