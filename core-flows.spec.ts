import { test, expect, Page } from '@playwright/test';
import {
  cleanupPlaywrightData,
  login,
  openMenu,
  seedAppointment,
  seedCareTeam,
  seedPrescription,
  seedUser,
  uniqueId,
} from './e2e.helpers';

async function chooseComboboxOption(page: Page, label: string, option: string): Promise<void> {
  const combobox = page.getByLabel(label);
  await combobox.click();
  await combobox.fill(option);
  await page.getByRole('option', { name: option, exact: true }).click();
}

async function openAppointmentsPage(page: Page): Promise<void> {
  await openMenu(page);
  await page.getByRole('button', { name: /Appointment/ }).click();
  await expect(page.getByText('Book New Appointment')).toBeVisible();
}

test.describe.serial('Core MedMinder flows', () => {
  test.beforeAll(() => {
    cleanupPlaywrightData();
  });

  test.afterAll(() => {
    cleanupPlaywrightData();
  });

  test('signs up a new patient and can log in', async ({ page }) => {
    const id = uniqueId('signup');
    const email = `pw_${id}@example.com`;
    const password = 'playwright123';
    const name = 'Playwright Signup';

    await page.goto('/');
    await page.getByRole('button', { name: 'Sign Up' }).click();
    await page.getByRole('button', { name: 'Patient' }).click();

    await page.getByRole('textbox', { name: 'First Name *' }).fill('Playwright');
    await page.getByRole('textbox', { name: 'Last Name *' }).fill('Signup');
    await page.getByRole('textbox', { name: 'Address Line 1 *' }).fill('1 Signup Street');
    await page.getByRole('textbox', { name: 'City *' }).fill('Charlotte');
    await chooseComboboxOption(page, 'State *', 'North Carolina');
    await page.getByRole('textbox', { name: 'Zip Code *' }).fill('28223');
    await page.getByRole('textbox', { name: 'Phone *' }).fill('7045551212');
    await page.getByRole('textbox', { name: 'Email *' }).fill(email);
    await page.getByRole('textbox', { name: 'Password *' }).fill(password);
    await page.getByRole('button', { name: 'Sign Up' }).click();

    await expect(page.getByText('Select Your Role')).toBeVisible();
    await page.getByRole('tab', { name: 'Sign In' }).click();
    await page.getByRole('textbox', { name: 'Email' }).fill(email);
    await page.getByRole('textbox', { name: 'Password' }).fill(password);
    await page.getByRole('button', { name: 'Sign In' }).click();

    await expect(page.getByText(`Welcome back, ${name}!`)).toBeVisible();
    await expect(page.getByText(`Account: ${email}`)).toBeVisible();
    await expect(page.getByText('Role: Patient')).toBeVisible();
    await expect(page.getByText(name)).toBeVisible();
  });

  test('logs in as a seeded patient', async ({ page }) => {
    const id = uniqueId('login');
    const email = `pw_${id}@example.com`;
    const password = 'playwright123';
    const name = `Playwright ${id}`;

    seedUser({ email, password, name, role: 'Patient' });

    await login(page, email, password, name, 'Patient');
  });

  test('shows a patient booked appointments in the scheduler', async ({ page }) => {
    const id = uniqueId('booking');
    const patient = {
      email: `pw_patient_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Booking Patient ${id}`,
      role: 'Patient' as const,
    };
    const doctor = {
      email: `pw_doctor_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Booking Doctor ${id}`,
      role: 'Doctor' as const,
      speciality: 'Dentist',
    };

    seedUser(patient);
    seedUser(doctor);

    await login(page, patient.email, patient.password, patient.name, 'Patient');
    await openAppointmentsPage(page);
    await chooseComboboxOption(
      page,
      'Choose a doctor to view their availability:',
      `${doctor.name} (${doctor.speciality})`,
    );
    await expect(page.getByText('Quick Book')).toBeVisible();
    await expect(page.getByText(doctor.name).first()).toBeVisible();

    seedAppointment({
      patientEmail: patient.email,
      doctorEmail: doctor.email,
      date: '2026-04-10',
      time: '09:00',
    });

    await login(page, patient.email, patient.password, patient.name, 'Patient');
    await openAppointmentsPage(page);
    await expect(page.getByText(doctor.name).first()).toBeVisible();
    await expect(page.getByText('Total Upcoming Appointments: 1')).toBeVisible();
  });

  test('lets a doctor create a prescription for a linked patient', async ({ page }) => {
    const id = uniqueId('prescription');
    const patient = {
      email: `pw_patient_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Prescription Patient ${id}`,
      role: 'Patient' as const,
    };
    const doctor = {
      email: `pw_doctor_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Prescription Doctor ${id}`,
      role: 'Doctor' as const,
      speciality: 'Neurologist',
    };

    seedUser(patient);
    seedUser(doctor);
    seedCareTeam(patient.email, doctor.email);

    await login(page, doctor.email, doctor.password, doctor.name, 'Doctor');
    await page.getByRole('tab', { name: 'Prescriptions' }).click();
    await expect(page.getByText('Manage Prescriptions')).toBeVisible();
    await expect(page.getByText(patient.name, { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Prescribe' }).click();

    await expect(page.getByText('Create Prescription')).toBeVisible();
    await page.getByRole('textbox', { name: 'Diagnosis' }).fill('Seasonal allergies');
    await page.getByRole('textbox', { name: 'General Notes' }).fill('Stay hydrated and avoid triggers.');
    await page.getByRole('textbox', { name: 'Medicine Name 1' }).fill('Cetirizine');
    await page.getByRole('textbox', { name: 'Dosage 1' }).fill('10 mg');
    await page.getByRole('textbox', { name: 'Timing 1' }).fill('After breakfast');
    await page.getByRole('textbox', { name: 'Directions 1' }).fill('Take one tablet daily.');
    await page.getByRole('button', { name: 'Save Prescription' }).click();

    await expect(page.getByText(`Prescription saved for ${patient.name}.`)).toBeVisible();
  });

  test('lets a doctor add notes to a past appointment', async ({ page }) => {
    const id = uniqueId('notes');
    const patient = {
      email: `pw_patient_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Notes Patient ${id}`,
      role: 'Patient' as const,
    };
    const doctor = {
      email: `pw_doctor_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Notes Doctor ${id}`,
      role: 'Doctor' as const,
      speciality: 'General Practitioner',
    };

    seedUser(patient);
    seedUser(doctor);
    seedAppointment({
      patientEmail: patient.email,
      doctorEmail: doctor.email,
      date: '2025-04-08',
      time: '10:00',
    });

    await login(page, doctor.email, doctor.password, doctor.name, 'Doctor');
    await openMenu(page);
    await page.getByRole('button', { name: /Appointment/ }).click();
    await page.getByRole('tab', { name: 'Past Appointments' }).click();
    await expect(page.getByText(patient.name)).toBeVisible();
    await page.getByRole('button', { name: 'Add Notes' }).click();
    await page.getByRole('textbox', { name: 'Appointment notes' }).fill('Patient symptoms are improving. Continue monitoring.');
    await page.getByRole('button', { name: 'Save Note' }).click();

    await expect(page.getByText('Patient symptoms are improving. Continue monitoring.')).toBeVisible();
  });

  test('shows treatment summaries with prescriptions and doctor notes', async ({ page }) => {
    const id = uniqueId('summary');
    const patient = {
      email: `pw_patient_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Summary Patient ${id}`,
      role: 'Patient' as const,
    };
    const doctor = {
      email: `pw_doctor_${id}@example.com`,
      password: 'playwright123',
      name: `Playwright Summary Doctor ${id}`,
      role: 'Doctor' as const,
      speciality: 'Cardiologist',
    };

    seedUser(patient);
    seedUser(doctor);
    seedAppointment({
      patientEmail: patient.email,
      doctorEmail: doctor.email,
      date: '2025-03-15',
      time: '09:30',
      notes: 'Patient should continue daily walking and track blood pressure.',
    });
    seedPrescription({
      patientEmail: patient.email,
      patientName: patient.name,
      doctorEmail: doctor.email,
      diagnosis: 'Hypertension',
      followUpDays: 30,
      generalNotes: 'Blood pressure is responding well to treatment.',
      medicines: [
        {
          name: 'Lisinopril',
          dosage: '10 mg',
          frequency: 'Once daily',
          days: 30,
          route: 'Oral',
          timing: 'Morning',
          directions: 'Take one tablet every morning.',
        },
      ],
    });

    await login(page, patient.email, patient.password, patient.name, 'Patient');
    const summaryPanel = page.getByLabel('Treatment Summary');
    await expect(page.getByRole('heading', { name: 'Treatment Summary' })).toBeVisible();
    await expect(summaryPanel.getByText('Your care at a glance')).toBeVisible();
    await expect(summaryPanel.getByText('Hypertension', { exact: true })).toBeVisible();
    await expect(summaryPanel.getByText('Lisinopril', { exact: true })).toBeVisible();
    await expect(summaryPanel.getByText(`Dr. ${doctor.name} • Cardiologist`, { exact: true })).toBeVisible();
    await expect(summaryPanel.getByText('Blood pressure is responding well to treatment.')).toBeVisible();
    await expect(summaryPanel.getByText('Patient should continue daily walking and track blood pressure.')).toBeVisible();
  });
});
