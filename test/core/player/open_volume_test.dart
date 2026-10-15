import 'package:flutter_test/flutter_test.dart';
import 'package:media_core/media_core.dart';
import 'package:pure_live/core/player/kernel/open_volume.dart';

PlayerSource source([Map<String, Object?> metadata = const {}]) => PlayerSource(
  id: SourceId('volume-test'),
  uri: Uri.parse('https://example.invalid/live.m3u8'),
  metadata: metadata,
);

void main() {
  setUp(() => OpenVolume.pending = null);
  tearDown(() => OpenVolume.pending = null);

  test('an undeclared source leaves the engine volume unchanged', () {
    expect(OpenVolume.resolve(source()), isNull);
  });

  test('saved room volume survives fallback source attempts', () {
    OpenVolume.pending = 0.25;
    expect(OpenVolume.resolve(source()), 0.25);
    expect(OpenVolume.resolve(source()), 0.25);
    expect(OpenVolume.pending, 0.25);
  });

  test('per-cell mute overrides the saved room volume', () {
    OpenVolume.pending = 0.75;
    expect(OpenVolume.resolve(source({OpenVolume.metadataKey: 0})), 0.0);
    expect(OpenVolume.pending, 0.75);
  });

  test('per-source volume is clamped to the supported range', () {
    expect(OpenVolume.resolve(source({OpenVolume.metadataKey: -1})), 0.0);
    expect(OpenVolume.resolve(source({OpenVolume.metadataKey: 2})), 1.0);
    expect(OpenVolume.resolve(source({OpenVolume.metadataKey: 0.4})), 0.4);
  });

  test('non-numeric metadata falls back to the declared room volume', () {
    OpenVolume.pending = 0.5;
    expect(OpenVolume.resolve(source({OpenVolume.metadataKey: 'invalid'})), 0.5);
  });
}
