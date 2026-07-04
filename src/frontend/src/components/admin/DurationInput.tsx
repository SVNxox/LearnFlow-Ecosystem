'use client';

import { useState, useEffect } from 'react';

export interface DurationInputProps {
  value: number | null | undefined; // значение в секундах
  onChange: (seconds: number | null) => void;
  label?: string;
  disabled?: boolean;
}

type TimeUnit = 'seconds' | 'minutes' | 'hours';

export default function DurationInput({ value, onChange, label, disabled }: DurationInputProps) {
  // Выбираем удобную единицу автоматически
  const getInitialUnit = (seconds: number | null | undefined): TimeUnit => {
    if (!seconds || seconds === 0) return 'minutes';
    if (seconds < 60) return 'seconds';
    if (seconds < 3600) return 'minutes';
    return 'hours';
  };

  const [unit, setUnit] = useState<TimeUnit>(() => getInitialUnit(value));
  const [displayValue, setDisplayValue] = useState<string>(() => {
    if (!value || value === 0) return '';
    switch (getInitialUnit(value)) {
      case 'seconds': return String(value);
      case 'minutes': return String(Math.round(value / 60));
      case 'hours': return String(Math.round(value / 3600 * 10) / 10);
    }
  });

  // Обновляем displayValue при изменении value извне
  useEffect(() => {
    if (value === null || value === undefined) {
      setDisplayValue('');
      return;
    }

    const currentUnit = getInitialUnit(value);
    setUnit(currentUnit);

    switch (currentUnit) {
      case 'seconds':
        setDisplayValue(String(value));
        break;
      case 'minutes':
        setDisplayValue(String(Math.round(value / 60)));
        break;
      case 'hours':
        const hours = value / 3600;
        setDisplayValue(String(Math.round(hours * 10) / 10));
        break;
    }
  }, [value]);

  const convertToSeconds = (displayVal: string, timeUnit: TimeUnit): number | null => {
    if (!displayVal.trim()) return null;
    const num = parseFloat(displayVal);
    if (isNaN(num) || num < 0) return null;

    switch (timeUnit) {
      case 'seconds': return Math.round(num);
      case 'minutes': return Math.round(num * 60);
      case 'hours': return Math.round(num * 3600);
    }
  };

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDisplay = e.target.value;
    setDisplayValue(newDisplay);

    const seconds = convertToSeconds(newDisplay, unit);
    onChange(seconds);
  };

  const handleUnitChange = (newUnit: TimeUnit) => {
    // Конвертируем текущее значение в новую единицу
    const currentSeconds = convertToSeconds(displayValue, unit);
    setUnit(newUnit);

    if (currentSeconds === null) {
      setDisplayValue('');
      return;
    }

    switch (newUnit) {
      case 'seconds':
        setDisplayValue(String(currentSeconds));
        break;
      case 'minutes':
        setDisplayValue(String(Math.round(currentSeconds / 60)));
        break;
      case 'hours':
        const hours = currentSeconds / 3600;
        setDisplayValue(String(Math.round(hours * 10) / 10));
        break;
    }

    // onChange вызывается автоматически через handleValueChange
    onChange(currentSeconds);
  };

  const unitLabels = {
    seconds: 'сек',
    minutes: 'мин',
    hours: 'час',
  };

  return (
    <div>
      {label && (
        <label className="block text-xs font-medium text-foreground mb-1 font-body">
          {label}
        </label>
      )}
      <div className="flex gap-2">
        <input
          type="number"
          min="0"
          step={unit === 'hours' ? '0.1' : '1'}
          value={displayValue}
          onChange={handleValueChange}
          disabled={disabled}
          className="input flex-1"
          placeholder="0"
        />
        <select
          value={unit}
          onChange={(e) => handleUnitChange(e.target.value as TimeUnit)}
          disabled={disabled}
          className="input w-24"
        >
          <option value="seconds">{unitLabels.seconds}</option>
          <option value="minutes">{unitLabels.minutes}</option>
          <option value="hours">{unitLabels.hours}</option>
        </select>
      </div>
      {displayValue && (
        <p className="text-xs text-muted-foreground mt-1 font-mono">
          = {value || 0} soniya
        </p>
      )}
    </div>
  );
}