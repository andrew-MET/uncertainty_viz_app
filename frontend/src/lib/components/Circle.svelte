<script>
  let w = $state(0)
  let { h = 300 } = $props()
</script>

<svg bind:clientWidth={w} width="100%" height="{h}">
  <g fill="#B7410E" stroke="#A73100" stroke-width="27">
    <circle cx="{w / 2}" cy="{h / 2}" r="{w > h ? h / 3 : w / 3}"/>
  </g>
</svg>
