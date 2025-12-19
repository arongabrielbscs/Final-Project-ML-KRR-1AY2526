<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// --- STATE ---
const step = ref(0)
const errorMsg = ref('')
const result = ref(null)
const rawAnswers = reactive({})

// Final Profile
const userProfile = reactive({
  Name: '',
  Gender: '',
  ANXMAT: 0, BELONG: 0, TEACHSUP: 0, ESCS: 0, BULLIED: 0, ICTRES: 0
})

// --- 24 QUESTIONS (BuzzFeed / Vibe Check Edition) ---
const questions = [
  // ANXMAT (Math Anxiety)
  { category: 'ANXMAT', emoji: '💀', text: "It's 10 PM. You realize you have a Math assignment due tomorrow. Mood?", 
    options: [{ label: "Easy, I'll crush it", value: 1.0, icon: "😎" }, { label: "Ugh, dreading it", value: 2.5, icon: "😩" }, { label: "Panic mode activated", value: 4.0, icon: "🚨" }] },
  { category: 'ANXMAT', emoji: '👀', text: "Teacher says: 'Put your books away, surprise Math quiz!' You feel...", 
    options: [{ label: "Ready to flex", value: 1.0, icon: "💪" }, { label: "Nervous sweating", value: 3.0, icon: "💧" }, { label: "I might actually cry", value: 4.0, icon: "😭" }] },
  { category: 'ANXMAT', emoji: '📉', text: "Be honest: Do you think you're 'bad' at Math?", 
    options: [{ label: "Nah, I'm a wizard", value: 1.0, icon: "🧙‍♂️" }, { label: "I struggle a bit", value: 2.5, icon: "😕" }, { label: "Yes, it's my nemesis", value: 4.0, icon: "👿" }] },
  { category: 'ANXMAT', emoji: '🤢', text: "When you look at a page full of equations, your stomach goes...", 
    options: [{ label: "Chill / Hungry", value: 1.0, icon: "🍔" }, { label: "Tight / Tense", value: 2.5, icon: "🧶" }, { label: "Full nausea", value: 4.0, icon: "🤮" }] },

  // TEACHSUP (Teacher Support)
  { category: 'TEACHSUP', emoji: '🧐', text: "Real talk: Does your teacher actually care if you learn this stuff?", 
    options: [{ label: "Nope, they chillin'", value: -2.0, icon: "🧊" }, { label: "Sometimes", value: 0.0, icon: "🤷" }, { label: "Total wholesome support", value: 2.0, icon: "🥰" }] },
  { category: 'TEACHSUP', emoji: '🆘', text: "You're stuck on a problem. Does the teacher help?", 
    options: [{ label: "I'm on my own", value: -2.0, icon: "🏝️" }, { label: "If I beg them", value: 0.0, icon: "🥺" }, { label: "Yes, until I get it", value: 2.0, icon: "🦸" }] },
  { category: 'TEACHSUP', emoji: '🎤', text: "Can you share your opinion in class without getting roasted?", 
    options: [{ label: "No way, scary", value: -2.0, icon: "🤐" }, { label: "Depends on the day", value: 0.0, icon: "🌥️" }, { label: "Yeah, it's a safe space", value: 2.0, icon: "🛡️" }] },
  { category: 'TEACHSUP', emoji: '👻', text: "Does the teacher notice when you're struggling, or are you invisible?", 
    options: [{ label: "I'm invisible", value: -2.0, icon: "👻" }, { label: "They notice sometimes", value: 0.0, icon: "👀" }, { label: "They always check in", value: 2.0, icon: "🩺" }] },

  // BELONG (Sense of Belonging)
  { category: 'BELONG', emoji: '👽', text: "Social Vibe Check: Do you feel like an alien at school?", 
    options: [{ label: "Yes, total outsider", value: -2.0, icon: "🛸" }, { label: "I drift in and out", value: 0.0, icon: "🍃" }, { label: "No, I fit right in", value: 2.0, icon: "🧩" }] },
  { category: 'BELONG', emoji: '🤝', text: "Is making friends at this school easy?", 
    options: [{ label: "Impossible difficulty", value: -2.0, icon: "🧗" }, { label: "It's okay", value: 0.0, icon: "👌" }, { label: "Ez pz lemon squeezy", value: 2.0, icon: "🍋" }] },
  { category: 'BELONG', emoji: '🏰', text: "Do you feel like you 'belong' here?", 
    options: [{ label: "Nope, wrong planet", value: -2.0, icon: "🪐" }, { label: "I guess so?", value: 0.0, icon: "🤔" }, { label: "Yeah, this is my place", value: 2.0, icon: "📍" }] },
  { category: 'BELONG', emoji: '💖', text: "Do other students seem to like you?", 
    options: [{ label: "They ignore me", value: -2.0, icon: "🌵" }, { label: "Some do, some don't", value: 0.0, icon: "🌗" }, { label: "Yeah, I'm loved", value: 2.0, icon: "🌟" }] },

  // BULLIED (Exposure to Bullying)
  { category: 'BULLIED', emoji: '🚫', text: "Have people ghosted you or left you out on purpose?", 
    options: [{ label: "Yeah, happens a lot", value: 2.0, icon: "💔" }, { label: "Once or twice", value: 0.0, icon: "📅" }, { label: "Never", value: -2.0, icon: "✨" }] },
  { category: 'BULLIED', emoji: '🤡', text: "Has anyone made fun of you recently?", 
    options: [{ label: "Often", value: 2.0, icon: "🎭" }, { label: "Just teasing once", value: 0.0, icon: "🤏" }, { label: "Nope, I'm good", value: -2.0, icon: "😎" }] },
  { category: 'BULLIED', emoji: '🤬', text: "Has anyone actually threatened you at school?", 
    options: [{ label: "Yes, it's scary", value: 2.0, icon: "⚠️" }, { label: "A minor incident", value: 0.0, icon: "🔸" }, { label: "Never", value: -2.0, icon: "🕊️" }] },
  { category: 'BULLIED', emoji: '☕', text: "Any nasty rumors or 'tea' spread about you?", 
    options: [{ label: "All the time", value: 2.0, icon: "📢" }, { label: "Maybe once", value: 0.0, icon: "🤫" }, { label: "Zero drama", value: -2.0, icon: "🧘" }] },

  // ICTRES (Digital Resources)
  { category: 'ICTRES', emoji: '💻', text: "Tech Check: Do you have your OWN laptop for school?", 
    options: [{ label: "No device at all", value: -2.0, icon: "📵" }, { label: "I share with family", value: 0.0, icon: "👨‍👩‍👧" }, { label: "Yes, my own rig", value: 1.5, icon: "💻" }] },
  { category: 'ICTRES', emoji: '🐢', text: "How is your home internet situation?", 
    options: [{ label: "Laggy / Non-existent", value: -2.0, icon: "🐌" }, { label: "It works... mostly", value: 0.0, icon: "🐢" }, { label: "High-speed fiber", value: 1.0, icon: "🚀" }] },
  { category: 'ICTRES', emoji: '📱', text: "Do you have educational apps/software to help you?", 
    options: [{ label: "Nope", value: -2.0, icon: "❌" }, { label: "A couple", value: 0.0, icon: "📲" }, { label: "Yeah, fully loaded", value: 1.0, icon: "💾" }] },
  { category: 'ICTRES', emoji: '🎧', text: "Can you find a quiet place to study at home?", 
    options: [{ label: "It's a zoo here", value: -1.0, icon: "🐒" }, { label: "Sometimes", value: 0.5, icon: "🤷" }, { label: "Yes, total silence", value: 1.0, icon: "🤫" }] },

  // ESCS (Wealth Proxy)
  { category: 'ESCS', emoji: '📚', text: "Aesthetic check: How many books are in your house?", 
    options: [{ label: "0-10 (Minimalist)", value: -2.0, icon: "📄" }, { label: "A shelf or two", value: 0.0, icon: "📚" }, { label: "A whole library", value: 2.0, icon: "🏛️" }] },
  { category: 'ESCS', emoji: '🚗', text: "Does your family own a car?", 
    options: [{ label: "No / Public Transpo", value: -1.0, icon: "🚌" }, { label: "Yes, we have wheels", value: 1.0, icon: "🚗" }] },
  { category: 'ESCS', emoji: '🚪', text: "Do you have your own bedroom?", 
    options: [{ label: "No, I share", value: -1.0, icon: "👯" }, { label: "Yes, my sanctuary", value: 1.0, icon: "🛌" }] },
  { category: 'ESCS', emoji: '💸', text: "Real talk: How's the money situation at home?", 
    options: [{ label: "It's a struggle", value: -2.0, icon: "⛈️" }, { label: "We get by okay", value: 0.0, icon: "☁️" }, { label: "We're comfortable", value: 2.0, icon: "☀️" }] },
]

// --- LOGIC ---
const currentQuestion = computed(() => questions[step.value - 1])
const progressValue = computed(() => ((step.value - 1) / questions.length) * 100)

const selectAnswer = (value) => {
  rawAnswers[step.value - 1] = value
  setTimeout(() => {
    step.value++
    if (step.value > questions.length) calculateAndSubmit()
  }, 150)
}

const calculateAndSubmit = async () => {
  step.value = 99
  errorMsg.value = ''
  
  // Aggregate Scores
  const sums = { ANXMAT: [], BELONG: [], TEACHSUP: [], ESCS: [], BULLIED: [], ICTRES: [] }
  questions.forEach((q, index) => {
    const ans = rawAnswers[index]
    if (ans !== undefined) sums[q.category].push(ans)
  })

  for (const key in sums) {
    if (sums[key].length > 0) {
      userProfile[key] = parseFloat((sums[key].reduce((a, b) => a + b, 0) / sums[key].length).toFixed(2))
    }
  }

  try {
    // NEW
    // const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    // const response = await axios.post(`${apiUrl}/analyze`, userProfile);
    const response = await axios.post('/analyze', userProfile)
    result.value = response.data
    step.value = 100
  } catch (err) {
    console.error(err)
    errorMsg.value = "Brain Disconnected! Is backend running?"
    step.value = 0
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4 font-sans text-slate-100">
    
    <div class="w-full max-w-lg md:max-w-2xl transition-all duration-300">
      
      <div v-if="step === 0" class="text-center space-y-8 animate-in fade-in zoom-in duration-500">
        <div class="bg-indigo-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/50">
          <span class="text-4xl">🧠</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-black tracking-tight">The "Vibe Check"</h1>
        <p class="text-slate-400 text-lg">An AI-powered academic personality test.</p>
        
        <Card class="bg-slate-800 border-slate-700 p-6 text-left">
          <div class="space-y-4">
            <div>
              <label class="text-sm font-bold text-slate-400 uppercase">Your Name</label>
              <Input v-model="userProfile.Name" placeholder="e.g. Juan" class="bg-slate-900 border-slate-600 text-white mt-1 h-12" />
            </div>
            <div>
              <label class="text-sm font-bold text-slate-400 uppercase">Gender</label>
              <Select v-model="userProfile.Gender">
                <SelectTrigger class="bg-slate-900 border-slate-600 text-white mt-1 h-12">
                  <SelectValue placeholder="Select..." />
                </SelectTrigger>
                <SelectContent class="bg-slate-800 border-slate-600 text-white">
                  <SelectItem value="Male">Male</SelectItem>
                  <SelectItem value="Female">Female</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        <Button 
          @click="userProfile.Gender ? step++ : null"
          :disabled="!userProfile.Gender"
          class="w-full py-8 text-xl font-bold bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl shadow-xl shadow-indigo-900/20 transition-all hover:scale-105 active:scale-95">
          Start Quiz 🚀
        </Button>
      </div>

      <div v-if="step >= 1 && step <= questions.length" class="space-y-6">
        <div class="flex justify-between items-end px-2">
          <span class="text-sm font-bold text-indigo-400 tracking-widest uppercase">Question {{ step }} / {{ questions.length }}</span>
          <span class="text-xs text-slate-500 font-mono">{{ currentQuestion.category }}</span>
        </div>
        
        <Progress :model-value="progressValue" class="h-4 rounded-full bg-slate-800 [&>div]:bg-indigo-500" />

        <Card class="bg-slate-800 border-slate-700 shadow-2xl overflow-hidden mt-6">
          <CardHeader class="text-center py-10 bg-slate-800/50">
            <div class="text-6xl mb-6 animate-bounce">{{ currentQuestion.emoji }}</div>
            <CardTitle class="text-2xl md:text-3xl font-bold leading-tight text-white">
              {{ currentQuestion.text }}
            </CardTitle>
          </CardHeader>
          
          <CardContent class="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              v-for="opt in currentQuestion.options" 
              :key="opt.label"
              @click="selectAnswer(opt.value)"
              class="group relative flex flex-col items-center justify-center p-6 h-40 bg-slate-700 hover:bg-indigo-600 rounded-2xl border-2 border-slate-600 hover:border-indigo-400 transition-all duration-200 hover:-translate-y-1 shadow-lg active:scale-95">
              <span class="text-4xl mb-3 group-hover:scale-110 transition-transform">{{ opt.icon }}</span>
              <span class="font-bold text-lg text-slate-200 group-hover:text-white">{{ opt.label }}</span>
            </button>
          </CardContent>
        </Card>
      </div>

      <div v-if="step === 99" class="text-center py-20 space-y-6">
        <div class="w-24 h-24 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <h2 class="text-2xl font-bold animate-pulse">Consulting the Oracle...</h2>
      </div>

      <div v-if="step === 100 && result" class="animate-in slide-in-from-bottom-10 duration-700">
        <Card class="bg-white text-slate-900 border-0 shadow-2xl overflow-hidden">
          
          <div :class="{
              'bg-emerald-500': result.advisory.color === 'green',
              'bg-rose-500': result.advisory.color === 'red',
              'bg-amber-500': result.advisory.color === 'orange',
              'bg-blue-500': result.advisory.color === 'blue'
            }" class="p-8 text-center text-white relative overflow-hidden">
            
            <div class="absolute inset-0 opacity-10 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]"></div>
            
            <div class="relative z-10">
              <Badge class="bg-white/20 hover:bg-white/30 text-white border-0 px-6 py-2 uppercase tracking-widest mb-4 shadow-lg backdrop-blur-sm">
                {{ result.advisory.status }}
              </Badge>
              <h1 class="text-3xl md:text-5xl font-black mb-2 tracking-tight">
                {{ result.name ? result.name : 'Student' }}
              </h1>
              <p class="text-lg md:text-xl opacity-95 font-medium max-w-lg mx-auto leading-relaxed">
                {{ result.advisory.message }}
              </p>
            </div>
          </div>

          <CardContent class="p-6 space-y-8">
            
            <div>
              <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 text-center">
                Predicted Failure Risk
              </h3>
              <div class="grid grid-cols-3 gap-2 md:gap-4">
                <div class="bg-slate-50 p-3 md:p-4 rounded-xl text-center border border-slate-200 transition-all hover:bg-slate-100 hover:scale-105">
                  <div class="text-2xl mb-1">📐</div>
                  <div class="text-[10px] md:text-xs font-bold text-slate-400 uppercase">Math</div>
                  <div :class="result.neural_risks.PV1MATH > 50 ? 'text-rose-600' : 'text-emerald-600'" 
                       class="text-2xl md:text-4xl font-black tracking-tighter">
                    {{ Math.round(result.neural_risks.PV1MATH) }}%
                  </div>
                </div>
                <div class="bg-slate-50 p-3 md:p-4 rounded-xl text-center border border-slate-200 transition-all hover:bg-slate-100 hover:scale-105">
                  <div class="text-2xl mb-1">📖</div>
                  <div class="text-[10px] md:text-xs font-bold text-slate-400 uppercase">Reading</div>
                  <div :class="result.neural_risks.PV1READ > 50 ? 'text-rose-600' : 'text-emerald-600'" 
                       class="text-2xl md:text-4xl font-black tracking-tighter">
                    {{ Math.round(result.neural_risks.PV1READ) }}%
                  </div>
                </div>
                <div class="bg-slate-50 p-3 md:p-4 rounded-xl text-center border border-slate-200 transition-all hover:bg-slate-100 hover:scale-105">
                  <div class="text-2xl mb-1">🧬</div>
                  <div class="text-[10px] md:text-xs font-bold text-slate-400 uppercase">Science</div>
                  <div :class="result.neural_risks.PV1SCIE > 50 ? 'text-rose-600' : 'text-emerald-600'" 
                       class="text-2xl md:text-4xl font-black tracking-tighter">
                    {{ Math.round(result.neural_risks.PV1SCIE) }}%
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-indigo-50 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between border border-indigo-100 relative overflow-hidden">
              <div class="absolute right-0 top-0 opacity-10 text-9xl transform translate-x-10 -translate-y-10">🧠</div>
              <div class="z-10 text-center md:text-left mb-4 md:mb-0">
                <div class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-1">
                  Psychosocial Stress Level
                </div>
                <div class="text-sm text-indigo-900/70 max-w-xs">
                  Combined score of Anxiety, Belonging, and Teacher Support.
                </div>
              </div>
              <div class="z-10 flex items-center gap-3">
                <span class="text-4xl md:text-5xl font-black tracking-tighter"
                      :class="result.fuzzy_score > 60 ? 'text-rose-600' : 'text-indigo-600'">
                  {{ Math.round(result.fuzzy_score) }}
                </span>
                <span class="text-xs font-bold text-indigo-300 uppercase rotate-90 origin-left translate-y-2">
                  / 100
                </span>
              </div>
            </div>

            <div v-if="result.advisory.flags.length" class="space-y-3 pt-2">
              <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Identified Risk Factors
              </h3>
              <div class="flex flex-wrap gap-2">
                <span v-for="flag in result.advisory.flags" :key="flag" 
                      class="px-4 py-1.5 bg-slate-100 text-slate-600 font-bold text-xs rounded-full border border-slate-200">
                  #{{ flag }}
                </span>
              </div>
            </div>

            <Button @click="step = 0" class="w-full py-6 text-lg font-bold bg-slate-900 text-white hover:bg-slate-800 shadow-xl shadow-slate-900/10">
              Start New Assessment 🔄
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>