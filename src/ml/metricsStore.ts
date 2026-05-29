export interface EpisodeMetrics {
  episode: number;
  totalReward: number;
  goals: number;
  collisions: number;
  steps: number;
  aliveAtEnd: number;
}

class MetricsStore extends EventTarget {
  private _episodes: EpisodeMetrics[] = [];

  push(m: EpisodeMetrics) {
    this._episodes.push(m);
    this.dispatchEvent(new CustomEvent('update', { detail: [...this._episodes] }));
  }

  get episodes(): EpisodeMetrics[] {
    return this._episodes;
  }

  clear() {
    this._episodes = [];
    this.dispatchEvent(new CustomEvent('update', { detail: [] }));
  }
}

export const metricsStore = new MetricsStore();
