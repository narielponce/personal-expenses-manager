import { ref, onMounted, onUnmounted, computed } from 'vue';

export function useBreakpoints() {
  const windowWidth = ref(window.innerWidth);

  const onResize = () => {
    windowWidth.value = window.innerWidth;
  };

  onMounted(() => {
    window.addEventListener('resize', onResize);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', onResize);
  });

  const isMobile = computed(() => windowWidth.value < 768);
  const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024);
  const isDesktop = computed(() => windowWidth.value >= 1024);

  return {
    windowWidth,
    isMobile,
    isTablet,
    isDesktop
  };
}
