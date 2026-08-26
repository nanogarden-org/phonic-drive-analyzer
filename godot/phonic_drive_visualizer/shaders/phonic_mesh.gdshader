shader_type spatial;
render_mode unshaded, cull_disabled, wireframe;

uniform float drive_time = 0.0;
uniform float energy = 0.0;
uniform float brightness = 0.0;
uniform float stereo_width = 0.0;
uniform float transition_strength = 0.0;
uniform float compression = 0.0;
uniform float coherence = 0.0;
uniform float motif_activity = 0.0;
uniform float recurrence = 0.0;

void vertex() {
    vec3 p = VERTEX;
    float radial = length(p.xz);
    float wave_a = sin((p.x * (2.0 + brightness * 5.0)) + drive_time * 1.5);
    float wave_b = cos((p.z * (2.0 + coherence * 4.0)) - drive_time * 0.9);
    float motif_wave = sin((p.x + p.z) * (3.0 + recurrence * 7.0) + drive_time);

    float displacement = 0.22 * wave_a * (0.25 + energy);
    displacement += 0.18 * wave_b * (0.15 + stereo_width);
    displacement += 0.14 * motif_wave * motif_activity;

    float pinch = 1.0 - compression * exp(-radial * radial * 0.45) * 0.45;
    p.xz *= pinch;

    float twist = transition_strength * 0.55 * sin(p.z * 0.7 + drive_time * 0.6);
    float c = cos(twist);
    float s = sin(twist);
    p.xz = mat2(vec2(c, -s), vec2(s, c)) * p.xz;

    p.y += displacement;
    VERTEX = p;
}

void fragment() {
    vec3 cool = vec3(0.24, 0.48, 1.0);
    vec3 warm = vec3(0.78, 0.34, 1.0);
    vec3 color = mix(cool, warm, clamp(brightness * 0.6 + motif_activity * 0.4, 0.0, 1.0));
    float pulse = 0.55 + transition_strength * 0.35 + recurrence * 0.1;
    ALBEDO = color * pulse;
    EMISSION = color * (0.3 + transition_strength * 0.7);
}
