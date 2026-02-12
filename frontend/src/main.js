import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap' // This imports the JS part of Bootstrap, make sure it's correct for your needs (e.g., if you need Popper.js, you might need to install it separately and import it)

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
