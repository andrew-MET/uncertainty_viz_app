<script>
  
  import '@fontsource-variable/winky-sans';
	import { style } from 'd3';
  let { children } = $props()

</script>

{@render children()}

<style>
	:global(body) {
    font-family: 'Winky Sans Variable', sans-serif;
  }
</style>