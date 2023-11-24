<pre class="mermaid">
  classDiagram
  Animal <|-- Duck
  Animal <|-- Fish
  Animal <|-- Zebra
  Animal : +int age
  Animal : +String gender
  Animal: +isMammal()
  Animal: +mate()
  class Duck{
    +String beakColor
    +swim()
    +quack()
    }
  class Fish{
    -int sizeInFeet
    -canEat()
    }
  class Zebra{
    +bool is_wild
    +run()
    }

    callback Duck callback "Tooltip"
    link Zebra "https://www.github.com" "This is a link"
</pre>

<script>
  const callback = function () {
    alert('A callback was triggered');
  };
  const config = {
    startOnLoad: true,
    securityLevel: 'loose',
  };
  mermaid.initialize(config);
</script>