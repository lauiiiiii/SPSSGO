import { onMounted } from 'vue'

export function useScrollReveal(selector = '.anim') {
  onMounted(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('anim-visible')
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: 0.12 })

    document.querySelectorAll(selector).forEach(el => observer.observe(el))
  })
}
