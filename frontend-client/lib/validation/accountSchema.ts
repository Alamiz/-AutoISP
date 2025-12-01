import * as Yup from "yup";

export const accountSchema = Yup.object().shape({
  email: Yup.string().email("Invalid email").required("Required"),
  password: Yup.string().min(6, "Minimum 6 characters").required("Required"),
  label: Yup.string().max(50, "Maximum 50 characters"),

  // New fields
  provider: Yup.string().oneOf(["gmx", "webde"], "Invalid provider").required("Required"),
  type: Yup.string().oneOf(["desktop", "mobile"], "Invalid type").required("Required"),

  recovery_email: Yup.string().email("Invalid email").nullable(),
  number: Yup.string().nullable(),

  proxy_host: Yup.string().nullable(),
  proxy_port: Yup.number().nullable().transform((value) => (isNaN(value) ? undefined : value)),
  proxy_username: Yup.string().nullable(),
  proxy_password: Yup.string().nullable(),
  proxy_protocol: Yup.string().oneOf(["http", "https"], "Invalid protocol").nullable(),
});
