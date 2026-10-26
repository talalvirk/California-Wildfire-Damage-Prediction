import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { App } from './app';
import { FEATURES } from './feature-schema';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient()],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should define all 21 model features', () => {
    expect(FEATURES.length).toBe(21);
  });

  it('should be invalid when empty and valid after loading the sample', () => {
    const app = TestBed.createComponent(App).componentInstance;
    expect(app.form.valid).toBe(false);
    app.loadSample();
    expect(app.form.valid).toBe(true);
  });
});