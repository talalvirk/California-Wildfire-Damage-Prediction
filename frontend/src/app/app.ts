import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';

import { FEATURES, GROUPS, SAMPLE, Feature } from './feature-schema';
import { PredictionResponse, PredictionService } from './prediction.service';

@Component({
  selector: 'app-root',
  imports: [ReactiveFormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private service = inject(PredictionService);

  readonly groups = GROUPS;
  readonly features = FEATURES;

  readonly form = new FormGroup<Record<string, FormControl<number | null>>>(
    Object.fromEntries(
      FEATURES.map((f) => {
        const validators = [];
        if (f.required) validators.push(Validators.required);
        if (f.min !== undefined) validators.push(Validators.min(f.min));
        if (f.max !== undefined) validators.push(Validators.max(f.max));
        return [f.name, new FormControl<number | null>(null, validators)];
      }),
    ),
  );

  // GitHub Pages hosts only the static page: there is no Flask server there.
  // Live prediction therefore only works when the page is opened from localhost.
  readonly staticMode = !['localhost', '127.0.0.1'].includes(window.location.hostname);

  readonly loading = signal(false);
  readonly result = signal<PredictionResponse | null>(null);
  readonly errorMessage = signal<string | null>(null);

  featuresIn(group: string): Feature[] {
    return FEATURES.filter((f) => f.group === group);
  }

  invalid(name: string): boolean {
    const c = this.form.controls[name];
    return c.invalid && (c.touched || c.dirty);
  }

  fieldError(f: Feature): string {
    const e = this.form.controls[f.name].errors;
    if (!e) return '';
    if (e['required']) return 'Required';
    if (e['min']) return `Must be at least ${f.min}`;
    if (e['max']) return `Must be at most ${f.max}`;
    return 'Invalid value';
  }

  loadSample(): void {
    this.form.setValue(SAMPLE as Record<string, number | null>);
    this.result.set(null);
    this.errorMessage.set(null);
  }

  reset(): void {
    this.form.reset();
    this.result.set(null);
    this.errorMessage.set(null);
  }

  submit(): void {
    if (this.staticMode) return;
    this.form.markAllAsTouched();
    if (this.form.invalid) {
      this.errorMessage.set('Please fix the highlighted fields.');
      return;
    }
    const payload: Record<string, number | null> = {};
    for (const f of FEATURES) {
      payload[f.name] = this.form.controls[f.name].value;
    }

    this.loading.set(true);
    this.result.set(null);
    this.errorMessage.set(null);

    this.service.predict(payload).subscribe({
      next: (res) => {
        this.result.set(res);
        this.loading.set(false);
      },
      error: (err: HttpErrorResponse) => {
        this.loading.set(false);
        if (err.status === 0) {
          this.errorMessage.set(
            'Cannot reach the prediction API. Make sure Flask is running (python backend\\app.py).',
          );
        } else if (err.status === 400 && err.error?.error) {
          const details = err.error.fields ? ' ' + JSON.stringify(err.error.fields) : '';
          this.errorMessage.set(`The API rejected the input: ${err.error.error}.${details}`);
        } else {
          this.errorMessage.set(`Server error (HTTP ${err.status}). Check the Flask terminal.`);
        }
      },
    });
  }

  percent(p: number): string {
    return (p * 100).toFixed(1) + '%';
  }
}