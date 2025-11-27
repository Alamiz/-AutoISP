import * as Yup from "yup";

export const accountSchema = Yup.object().shape({
  email: Yup.string().email("Invalid email").required("Required"),
  password: Yup.string().min(6, "Minimum 8 characters").required("Required"),
  label: Yup.string().max(50, "Maximum 20 characters"),
});
